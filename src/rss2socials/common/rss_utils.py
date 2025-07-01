import os
import time
import feedparser
from datetime import datetime, timezone
from typing import Any, Set, Tuple, Optional

__all__ = [
    "fetch_rss_entries",
    "parse_entry_link_and_date",
    "load_seen_links",
    "save_seen_links"
]


def fetch_rss_entries(feed_url: str) -> Any:
    """
    Parse the RSS feed and return its entries.

    Args:
        feed_url: The URL of the RSS feed.

    Returns:
        The entries from the parsed feed.
    """
    feed = feedparser.parse(feed_url)
    return feed.entries


def parse_entry_link_and_date(entry: Any) -> Tuple[str, Optional[datetime]]:
    """
    Extract the link and publication date from an RSS entry.

    Args:
        entry: The RSS entry object.

    Returns:
        A tuple of (link, publication datetime or None).
    """
    link = entry.get("link", "")
    published_parsed = entry.get("published_parsed", None)
    pub_date = None
    # Check for 'published_parsed' or 'updated_parsed'
    if not published_parsed:
        published_parsed = entry.get("updated_parsed", None)
    if published_parsed and isinstance(published_parsed, time.struct_time):
        pub_date = datetime.fromtimestamp(
            time.mktime(published_parsed), tz=timezone.utc)
    return link, pub_date


def load_seen_links(SEEN_FILE: str) -> Set[str]:
    """
    Load the set of seen links from the deduplication file(s).

    Args:
        SEEN_FILE: Path to the current deduplication file.

    Returns:
        A set of seen links.
    """
    import logging
    if os.path.exists(SEEN_FILE):
        try:
            with open(SEEN_FILE, "r") as f:
                seen = set(line.strip() for line in f if line.strip())
            logging.debug(f"[rss_utils] Loaded {len(seen)} seen links from {SEEN_FILE}")
            return seen
        except Exception as e:
            logging.error(f"[rss_utils] Error reading seen links from {SEEN_FILE}: {e}")
            return set()
    logging.debug(f"[rss_utils] Seen file {SEEN_FILE} does not exist; starting with empty set.")
    return set()


def save_seen_links(seen_links: Set[str], SEEN_FILE: str) -> None:
    """
    Save the set of seen links to the deduplication file.

    Args:
        seen_links: Set of links to save.
        SEEN_FILE: Path to the deduplication file.
    """
    import logging
    try:
        with open(SEEN_FILE, "w") as f:
            for link in seen_links:
                f.write(link + "\n")
        logging.debug(f"[rss_utils] Saved {len(seen_links)} seen links to {SEEN_FILE}")
    except Exception as e:
        logging.error(f"[rss_utils] Error saving seen links to {SEEN_FILE}: {e}")
