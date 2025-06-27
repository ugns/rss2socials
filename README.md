# rss2socials

[![PyPI version](https://img.shields.io/pypi/v/rss2socials.svg)](https://pypi.org/project/rss2socials/)
[![Python versions](https://img.shields.io/pypi/pyversions/rss2socials.svg)](https://pypi.org/project/rss2socials/)
[![Build Status](https://github.com/ugns/rss2socials/actions/workflows/ci.yml/badge.svg)](https://github.com/ugns/rss2socials/actions/workflows/ci.yml)
[![Coverage Status](https://img.shields.io/codecov/c/github/ugns/rss2socials)](https://codecov.io/gh/ugns/rss2socials)
[![License: MIT](https://img.shields.io/github/license/ugns/rss2socials)](https://github.com/ugns/rss2socials/blob/main/LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/rss2socials.svg)](https://pypistats.org/packages/rss2socials)

**rss2socials** is a modular Python CLI tool that automatically posts new entries from an RSS or Atom feed to one or more social media platforms. It is designed to be easily extensible, robust, and safe for automation and CI/CD workflows.

## Features

- **Dynamic connector system:** Add new social media platforms by simply dropping a connector module in `src/rss2socials/connector/`.
- **Automatic deduplication:** Tracks posted links to avoid reposting.
- **OpenAI-powered summaries:** Generates concise, platform-appropriate summaries for each post.
- **Flexible CLI:** Configure via command-line arguments or environment variables.
- **Comprehensive logging:** Supports configurable log levels for debugging and automation.
- **Tested and maintainable:** 100% test coverage for core modules, with robust error handling.

## Installation

### From PyPI

```sh
pip install rss2socials
```

### From Source (Recommended for Development)

Clone the repository and install all dependencies (main + dev) using pip-tools and a pinned requirements file for reproducibility:

```sh
git clone https://github.com/ugns/rss2socials.git
cd rss2socials
pip install pip-tools
pip-compile --extra dev --strip-extras --output-file=requirements.txt pyproject.toml
pip install -r requirements.txt
```

- This will install the package in editable mode along with all development tools (pytest, flake8, etc.).
- You can also use `make dev` to automate these steps.

## Requirements

- **Python 3.9 or newer is required.**

## Usage

### Using the CLI Entrypoint

After installation, you can use the CLI entrypoint (if installed from PyPI or with pip):

```sh
rss2socials --feed-url https://example.com/feed.xml --platform bluesky
```

Or, if you prefer to use the Python module directly:

```sh
python -m rss2socials --feed-url https://example.com/feed.xml --platform bluesky
```

Both commands are equivalent and will invoke the CLI interface.

### As a Library

You can also use `rss2socials` as a Python library in your own scripts:

```python
from rss2socials.cli import main

# Call main() with sys.argv-style arguments
main([
    "--feed-url", "https://example.com/feed.xml",
    "--platform", "bluesky"
])
```

### CLI Options
- `--feed-url` (or `FEED_URL` env): RSS/Atom feed URL (required)
- `--platform`: One or more platforms to post to (default: bluesky; auto-discovers available platforms)
- `--seen-file`: File to track posted links (default: `seen_rss_posts.txt`)
- `--post-age-limit-days`: Only post entries newer than this many days (default: 7)
- `--log-level`: Logging level (default: INFO)

## Dynamic Connector System

To add support for a new social media platform:
1. Create a new Python file in `src/rss2socials/connector/` (e.g., `myplatform.py`).
2. Implement a `post(summary, link, fetch_page_metadata)` function and set a `PLATFORM` string (e.g., `PLATFORM = "myplatform"`).
3. Optionally, set `MAX_GRAPHEMES` for platform-specific length limits.

The CLI will automatically discover and make your platform available as a `--platform` option. No changes to the core code are required.

**Example connector skeleton:**
```python
PLATFORM = "myplatform"
MAX_GRAPHEMES = 300

def post(summary, link, fetch_page_metadata):
    # Implement posting logic here
    return True  # Return True if successful
```

## Environment Variables
- `OPENAI_API_KEY`: Required for summary generation
- `FEED_URL`, `SEEN_FILE`, `POST_AGE_LIMIT_DAYS`, `LOG_LEVEL`, `PLATFORM`: Optional, override CLI args
- **Connector-specific variables:**
  - For Bluesky:
    - `BLUESKY_HANDLE`: Your Bluesky username (required)
    - `BLUESKY_APP_PASSWORD`: Your Bluesky app password (required)
  - Other connectors may require their own environment variables; see the connector's documentation or source code for details.

## Development & Testing

- Install all dependencies: `make dev`
- Run tests: `make test` (uses tox for all supported Python versions)
- Lint: `make lint`
- Coverage: `make coverage`
- Add new connectors in `src/rss2socials/connector/`
- Regenerate constraints after dependency changes: `make freeze`

## License
MIT

## Contributing
Contributions are welcome! Please use [Conventional Commits](https://www.conventionalcommits.org/) and ensure all tests pass before submitting a PR.