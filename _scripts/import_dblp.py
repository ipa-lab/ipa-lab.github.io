#!/usr/bin/env python3
"""Import publications from a saved DBLP page into _data/publications/dblp_generated.yml.

DBLP blocks automated requests with a bot check, so this script works offline:

  1. Open https://dblp.org/pid/150/6416.html in your browser and save it
     (File > Save Page As..., "Web Page, HTML only" is enough).
  2. uv run _scripts/import_dblp.py "path/to/dblp_ Jürgen Cito.html"

Several files can be given (e.g. one per lab member). DBLP person XML files
(https://dblp.org/pid/<pid>.xml) are accepted too.
"""
import html
import os
import re
import sys
import xml.etree.ElementTree as ET

import yaml

OUTPUT_FILE = "_data/publications/dblp_generated.yml"

# Publication type constants (same values as DBLP's XML record types)
TYPE_INPROCEEDINGS = "inproceedings"
TYPE_ARTICLE = "article"
VENUE_CORR = "CoRR"

# DBLP's HTML entry classes -> XML record types. "informal" entries are CoRR
# preprints and similar, which the XML lists as <article>.
HTML_TYPES = {"informal": "article", "editor": "proceedings"}


def strip_tags(fragment):
    return " ".join(html.unescape(re.sub(r"<[^>]+>", "", fragment)).split())


def parse_html(text):
    """Yield publication dicts from a DBLP person page."""
    starts = [m.start() for m in re.finditer(r'<li class="entry ', text)] + [len(text)]
    for start, end in zip(starts, starts[1:]):
        entry = text[start:end]
        head = re.match(r'<li class="entry (\w+)[^"]*" id="([^"]+)"', entry)
        cite = re.search(r'(?s)<cite[^>]*>(.*?)</cite>', entry)
        if not head or not cite:
            continue
        kind, key = head.groups()
        cite = cite.group(1)

        authors = []
        for person in re.findall(r'(?s)<span itemprop="author".*?</span>(?:</a>)?', cite):
            # Linked co-authors carry their full DBLP name (with any " 0001"
            # suffix) in the title attribute; the page owner has plain text.
            title = re.search(r'itemprop="name" title="([^"]+)"', person)
            authors.append(html.unescape(title.group(1)) if title else strip_tags(person))

        title = re.search(r'(?s)<span class="title" itemprop="name">(.*?)</span>', cite)
        venue = re.search(r'(?s)itemprop="isPartOf"[^>]*><span itemprop="name">(.*?)</span>', cite)
        year = re.search(r'itemprop="datePublished">(\d{4})<', cite)
        url = re.search(r'<li class="ee"><a href="([^"]+)"', entry)

        yield {
            "id": key,
            "title": strip_tags(title.group(1)) if title else "",
            "year": int(year.group(1)) if year else None,
            "venue": strip_tags(venue.group(1)) if venue else "",
            "type": HTML_TYPES.get(kind, kind),
            "authors": authors,
            "url": html.unescape(url.group(1)) if url else f"https://dblp.org/rec/{key}",
        }


def text(elem, tag):
    t = elem.find(tag)
    return t.text.strip() if t is not None and t.text else ""


def parse_xml(document):
    """Yield publication dicts from a DBLP person XML file."""
    root = ET.fromstring(document)
    for r in root.findall("r"):
        entry = list(r)[0]
        key = entry.attrib.get("key")
        if not key:
            continue
        ee = next((e.text for e in entry.findall("ee") if e.text), None)
        yield {
            "id": key,
            "title": text(entry, "title"),
            "year": int(text(entry, "year")) if text(entry, "year").isdigit() else None,
            "venue": text(entry, "journal") or text(entry, "booktitle"),
            "type": entry.tag,
            "authors": [a.text for a in entry.findall("author") if a.text],
            "url": ee or f"https://dblp.org/rec/{key}",
        }


def normalize_title(title):
    """Normalize title for comparison by removing trailing punctuation and converting to lowercase."""
    return title.rstrip('.').lower()


def get_publication_priority(pub):
    """Lower is preferred: published papers, then CoRR preprints, then the rest; newer first."""
    year_score = -(pub["year"] or 0)
    if pub["type"] == TYPE_INPROCEEDINGS:
        return (0, year_score)
    if pub["type"] == TYPE_ARTICLE and pub["venue"] != VENUE_CORR:
        return (1, year_score)
    if pub["type"] == TYPE_ARTICLE and pub["venue"] == VENUE_CORR:
        return (2, year_score)
    return (3, year_score)


def deduplicate_publications(publications):
    """Keep one entry per normalized title (and per DBLP key), preferring the published version."""
    best_pubs = {}
    for pub in publications:
        normalized = normalize_title(pub["title"])
        existing = best_pubs.get(normalized)
        if existing is None or get_publication_priority(pub) < get_publication_priority(existing):
            if existing is not None and existing["id"] != pub["id"]:
                print(f"  Deduplicating '{pub['title']}': keeping {pub['venue']} over {existing['venue']}")
            best_pubs[normalized] = pub
    return list(best_pubs.values())


def main(paths):
    if not paths:
        sys.exit(__doc__)
    publications = []
    for path in paths:
        with open(path, encoding="utf-8") as f:
            document = f.read()
        parsed = list(parse_xml(document) if document.lstrip().startswith("<?xml") else parse_html(document))
        print(f"Read {len(parsed)} entries from {path}")
        publications.extend(parsed)

    publications = deduplicate_publications(publications)
    if not publications:
        sys.exit("No publications found; is this a saved DBLP person page? Nothing written.")
    publications.sort(key=lambda p: (-(p["year"] or 0), p["title"]))

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("# This file is generated by _scripts/import_dblp.py. Do not edit manually.\n")
        yaml.dump(publications, f, allow_unicode=True)
    print(f"Generated {OUTPUT_FILE} with {len(publications)} publications.")


if __name__ == "__main__":
    main(sys.argv[1:])
