# IPA Lab Website

The website of the Interactive Programming & Analysis Lab at TU Wien, served at <https://ipa-lab.github.io>.

It is a small static site: `build.py` loads YAML from `_data/`, renders the Jinja2 templates in `templates/`, and writes plain HTML to `_site/`. There is no JS or CSS framework; styles live in one hand-written `static/site.css`.

To open or close thesis supervision or advertise a position, edit `_data/site.yml` and rebuild. The home page and the Join page read from it.

## Install

You need [uv](https://docs.astral.sh/uv/). It installs Python and the dependencies (Jinja2, PyYAML, requests) from `pyproject.toml`:

```bash
uv sync
```

## Build

```bash
uv run build.py
```

To refresh the team data from TISS before building:

```bash
uv run build.py --fetch
```

## Preview

```bash
python -m http.server -d _site
```

Then open <http://localhost:8000>. Rebuild after editing a template or data file and reload the page.

## Where the content lives

| What | File |
| --- | --- |
| Page templates | `templates/*.html` (shared layout in `templates/base.html`) |
| Recruiting status (theses, projects, open positions) | `_data/site.yml` |
| "Questions we're working on" on the home page | `_data/questions.yml` |
| Research themes and their linked papers | `_data/research.yml` |
| Team members | `_data/team/tiss_generated.yml` (generated), with hand corrections in `_data/team/overrides.yml` |
| Teaching | `_data/teaching.yml` |
| Publications | `_data/publications/dblp_generated.yml` (generated) |
| Styles, images, scripts | `static/` (copied to `_site/static/`) |

## How the data is refreshed

Two scripts in `_scripts/` regenerate the YAML files. Don't edit the generated files by hand; they are overwritten on every run.

- **Publications are imported by hand.** DBLP blocks automated requests with a bot check, so there is no scraper. To refresh:
  1. Open <https://dblp.org/pid/150/6416.html> in your browser and save the page (File › Save Page As…).
  2. Run `uv run _scripts/import_dblp.py "path/to/saved page.html"`, then rebuild and commit `_data/publications/dblp_generated.yml`.

  The importer de-duplicates entries by title (keeping the published version over a preprint) and sorts them newest first. It also accepts several files (for example one per lab member) and DBLP XML files.
- `_scripts/fetch_tiss.py` fetches name, role, email, phone, office, and photo for the IDs in its `tiss_ids` list from the TU Wien TISS API and writes `_data/team/tiss_generated.yml`. To add or remove a team member, edit `tiss_ids`.

`build.py` then cleans the publication data while rendering: it strips DBLP disambiguation numbers from author names (`Satish Chandra 0001`), strips trailing periods from titles, shows the venue `CoRR` as `arXiv`, and classifies each entry as Conference, Journal, Preprint, Artifact, or Thesis. Lab members (anyone in the TISS data) are highlighted in author lists.

Team members are grouped by their TISS function group: professors as Faculty, student staff as Study assistants, and everyone else as Researchers. To add a person, add their TISS ID to `tiss_ids` in `_scripts/fetch_tiss.py`.

## Deployment

Every push to `master` runs `.github/workflows/pages.yml`, which sets up uv, refreshes the team data from TISS (`uv run build.py --fetch`), and deploys `_site/` to GitHub Pages. You can also start it by hand from the Actions tab.
