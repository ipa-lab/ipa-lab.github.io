# IPA-Lab Website

This is the official website for the Interactive Programming & Analysis Lab at TU Wien, built with [Jekyll](https://jekyllrb.com/).

## About Jekyll

This website is built using Jekyll, a static site generator that transforms plain text into static websites and blogs. Jekyll is particularly well-suited for GitHub Pages hosting.

For more information about Jekyll, see the [GitHub Pages Jekyll Tutorial](https://docs.github.com/en/pages/setting-up-a-github-pages-site-with-jekyll).

## Building Locally

To build and preview this Jekyll site locally, follow these steps:

### Prerequisites

- Ruby (version 2.7 or higher)
- RubyGems
- GCC and Make

### Installation Steps

1. Clone the repository:
   ```bash
   git clone https://github.com/ipa-lab/ipa-lab.github.io.git
   cd ipa-lab.github.io
   ```

2. Install the required gems:
   ```bash
   bundle install
   ```

3. Build and serve the site locally:
   ```bash
   bundle exec jekyll serve
   ```

4. Open your browser and navigate to:
   ```
   http://localhost:4000
   ```

The site will automatically rebuild when you make changes to the source files.

### Alternative: Watch Mode

For development, you can use the `--livereload` flag to automatically refresh the browser when changes are made:
```bash
bundle exec jekyll serve --livereload
```

## Python Scripts

This repository includes two Python scripts in the `_scripts/` directory for automating data fetching:

### 1. `fetch_dblp.py`

**Purpose:** Fetches publication data from DBLP (Digital Bibliography & Library Project).

**Functionality:**
- Retrieves publication information for specified researcher DBLP IDs
- Fetches data from the DBLP XML API for each researcher
- Extracts key information including title, year, venue, authors, and publication type
- Sorts publications by year (newest first) and title
- Generates a YAML file at `_data/publications/dblp_generated.yml`

**Configuration:** Edit the `dblp_ids` list in the script to add or remove researchers.

**Usage:**
```bash
python _scripts/fetch_dblp.py
```

### 2. `fetch_tiss.py`

**Purpose:** Fetches team member information from the TU Wien TISS (TU Wien Information Systems and Services) API.

**Functionality:**
- Retrieves detailed information about team members using their TISS IDs
- Fetches data including name, role, unit, email, phone, office location, and photo
- Processes employee information such as function, organizational unit, and room details
- Generates a YAML file at `_data/team/tiss_generated.yml`

**Configuration:** Edit the `tiss_ids` list in the script to add or remove team members.

**Usage:**
```bash
python _scripts/fetch_tiss.py
```

**Note:** Both scripts require internet connectivity and generate YAML files that are automatically used by the Jekyll site to display publications and team information.

## Project Structure

```
.
├── _config.yml         # Jekyll configuration
├── _data/              # Data files (YAML) for team and publications
├── _includes/          # Reusable HTML components
├── _layouts/           # Page templates
├── _pages/             # Individual pages (team, publications, etc.)
├── _scripts/           # Python utility scripts
├── css/                # Stylesheets
├── Gemfile             # Ruby dependencies
└── index.md            # Homepage content
```

## License

See the repository for license information.
