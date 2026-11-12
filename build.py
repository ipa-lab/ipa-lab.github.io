#!/usr/bin/env python3
"""Build the IPA Lab website.

    uv run build.py           # render templates/ + _data/ into _site/
    uv run build.py --fetch   # refresh the team data from TISS first

Publications come from a saved DBLP page: see _scripts/import_dblp.py.
"""
import argparse
import datetime
import hashlib
import re
import shutil
import subprocess
import sys
from collections import Counter
from itertools import groupby
from pathlib import Path
from urllib.parse import urlparse

import requests

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined

ROOT = Path(__file__).parent
DATA, TEMPLATES, STATIC, OUT = ROOT / "_data", ROOT / "templates", ROOT / "static", ROOT / "_site"
PHOTO_CACHE = ROOT / ".cache" / "photos"  # downloaded TISS photos (git-ignored)

# Privacy: the built site must not make visitors' browsers contact any other
# server (no fonts, images, scripts, or styles from elsewhere). Plain links are fine.
EXTERNAL_RESOURCE = re.compile(
    r'(?:src|srcset|poster)\s*=\s*["\']\s*(?:https?:)?//'
    r'|<link\b[^>]*\bhref\s*=\s*["\']\s*(?:https?:)?//'
    r'|url\(\s*["\']?\s*(?:https?:)?//'
    r'|@import\s+["\']?\s*(?:url\()?\s*["\']?\s*(?:https?:)?//',
    re.IGNORECASE)

# template -> output path (directory-style URLs work on GitHub Pages and http.server)
PAGES = {
    "index.html": "index.html",
    "research.html": "research/index.html",
    "team.html": "team/index.html",
    "publications.html": "publications/index.html",
    "join.html": "join/index.html",
    "404.html": "404.html",
}
REDIRECTS = {"vacancies/index.html": "/join/"}  # keep old Jekyll URLs alive

# TISS function groups: 1002 = professors, 1280 = student staff. Everyone else
# (staff scientists, externals) is listed as a researcher.
FACULTY_GROUPS, STUDENT_GROUPS = {1002}, {1280}
TYPE_ORDER = ["Conference", "Journal", "Preprint", "Artifact", "Thesis"]


def load(path):
    with open(DATA / path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def initials(name):
    parts = name.split()
    return (parts[0][0] + parts[-1][0]).upper() if parts else "?"


def load_team():
    overrides = load("team/overrides.yml") or {}
    team = []
    for tiss_id, p in load("team/tiss_generated.yml").items():
        p.update(overrides.get(tiss_id) or {})
        group = p.get("function_group_tiss_id")
        p["section"] = ("faculty" if group in FACULTY_GROUPS
                        else "assistants" if group in STUDENT_GROUPS else "researchers")
        p["initials"] = initials(p["name"])
        p["id"] = tiss_id
        team.append(p)
    return team


def name_key(name):
    parts = name.split()
    return (parts[0].lower(), parts[-1].lower()) if parts else ("", "")


def classify(pub):
    if pub["type"] == "data":
        return "Artifact"
    if pub["type"] in ("book", "phdthesis"):
        return "Thesis"
    if pub["venue"] == "CoRR":
        return "Preprint"
    return "Journal" if pub["type"] == "article" else "Conference"


def load_publications(team):
    members = {name_key(p["name"]) for p in team}
    pubs = []
    for raw in load("publications/dblp_generated.yml"):
        authors = [re.sub(r"\s+\d{4}$", "", a) for a in raw.get("authors") or []]
        pubs.append({
            "id": raw["id"],
            "title": (raw.get("title") or "").strip().rstrip("."),
            "year": raw.get("year"),
            "venue": "arXiv" if raw.get("venue") == "CoRR" else (raw.get("venue") or ""),
            "kind": classify(raw),
            "url": raw.get("url"),
            "authors": [{"name": a, "member": name_key(a) in members} for a in authors],
        })
    pubs.sort(key=lambda p: -(p["year"] or 0))  # stable: keeps DBLP order within a year
    return pubs


def attach_papers(items, pubs):
    """Resolve each item's `paper_matches` title fragments against the publication list."""
    for item in items:
        item["papers"] = []
        for fragment in item.get("paper_matches", []):
            hit = next((p for p in pubs if fragment.lower() in p["title"].lower()), None)
            if hit is None:
                print(f"warning: no publication matches '{fragment}'")
            else:
                item["papers"].append(hit)
    return items


def localize_photos(team):
    """Download remote (TISS) photos so the site serves them itself.

    Returns {filename: cached path}; each person's `picture` is rewritten to the
    local URL, or cleared (initials fallback) if the download fails.
    """
    PHOTO_CACHE.mkdir(parents=True, exist_ok=True)
    files = {}
    for p in team:
        url = p.get("picture") or ""
        if not url.startswith(("http://", "https://")):
            continue
        ext = Path(urlparse(url).path).suffix.lower() or ".jpg"
        name = f"{p['id']}-{hashlib.sha1(url.encode()).hexdigest()[:8]}{ext}"
        cached = PHOTO_CACHE / name
        if not cached.exists():
            try:
                resp = requests.get(url, timeout=15)
                resp.raise_for_status()
                if not resp.headers.get("content-type", "").startswith("image/"):
                    raise ValueError(f"not an image ({resp.headers.get('content-type')})")
                cached.write_bytes(resp.content)
            except Exception as err:  # keep building; the template shows initials
                print(f"warning: could not download photo for {p['name']}: {err}")
                p["picture"] = ""
                continue
        p["picture"] = f"/static/people/{name}"
        files[name] = cached
    return files


def check_no_external_resources():
    """Fail the build if any generated page or stylesheet loads a resource from another server."""
    problems = []
    for path in OUT.rglob("*"):
        if path.suffix in (".html", ".css", ".js") and path.is_file():
            for m in EXTERNAL_RESOURCE.finditer(path.read_text(encoding="utf-8")):
                problems.append(f"{path.relative_to(OUT)}: {m.group(0)}")
    if problems:
        sys.exit("error: external resources would leak visitor data to other servers:\n  "
                 + "\n  ".join(problems))


def fetch():
    """Refresh the team data from TISS, keeping the previous file if the fetch comes back empty."""
    for script, data in (("_scripts/fetch_tiss.py", "team/tiss_generated.yml"),):
        previous = (DATA / data).read_text(encoding="utf-8") if (DATA / data).exists() else None
        print(f"running {script}")
        subprocess.run([sys.executable, script], cwd=ROOT, check=True)
        if not load(data) and previous is not None:
            print(f"warning: {script} returned no entries; keeping the previous {data}")
            (DATA / data).write_text(previous, encoding="utf-8")


def build():
    team = load_team()
    photos = localize_photos(team)
    pubs = load_publications(team)
    context = {
        "team": team,
        "pubs": pubs,
        "pubs_by_year": [(y, list(g)) for y, g in groupby(pubs, key=lambda p: p["year"])],
        "type_counts": [(t, Counter(p["kind"] for p in pubs)[t]) for t in TYPE_ORDER],
        "themes": attach_papers(load("research.yml")["themes"], pubs),
        "questions": attach_papers(load("questions.yml")["questions"], pubs),
        "site": load("site.yml"),
        "teaching": load("teaching.yml")["courses"],
        "year": datetime.date.today().year,
    }

    env = Environment(loader=FileSystemLoader(TEMPLATES), autoescape=True,
                      undefined=StrictUndefined, trim_blocks=True, lstrip_blocks=True)
    if OUT.exists():
        shutil.rmtree(OUT)
    shutil.copytree(STATIC, OUT / "static")
    (OUT / "static" / "people").mkdir(parents=True, exist_ok=True)
    for name, cached in photos.items():
        shutil.copyfile(cached, OUT / "static" / "people" / name)

    for template, target in PAGES.items():
        path = OUT / target
        path.parent.mkdir(parents=True, exist_ok=True)
        page = template.removesuffix(".html")
        path.write_text(env.get_template(template).render(page=page, **context), encoding="utf-8")
    for target, url in REDIRECTS.items():
        path = OUT / target
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(env.get_template("redirect.html").render(url=url), encoding="utf-8")
    (OUT / ".nojekyll").touch()
    check_no_external_resources()
    print(f"built {len(PAGES)} pages, {len(pubs)} publications, {len(team)} people -> {OUT}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--fetch", action="store_true", help="refresh team data from TISS first")
    if parser.parse_args().fetch:
        fetch()
    build()
