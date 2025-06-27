import logging
from datetime import datetime, timezone, timedelta
from .common.rss_utils import fetch_rss_entries, parse_entry_link_and_date, load_seen_links, save_seen_links
from .common.openai_utils import generate_summary
from .common.metadata import fetch_page_metadata

__all__ = ["cli_main"]

logger = logging.getLogger("rss2socials.cli")


def discover_platforms(return_names_only=False):
    import importlib
    import pkgutil

    from . import connector

    dispatch = {}
    names = []
    for _, modname, ispkg in pkgutil.iter_modules(connector.__path__):
        if ispkg or modname.startswith("_"):
            continue
        try:
            mod = importlib.import_module(f".connector.{modname}", __package__)
            platform_name = getattr(mod, "PLATFORM", modname)
            names.append(platform_name)
            post_func = getattr(mod, "post", None)
            if callable(post_func):
                dispatch[platform_name] = lambda link, pf=post_func, pn=platform_name: pf(
                    generate_summary(pn.capitalize(), link, getattr(mod, "MAX_GRAPHEMES", 300)),
                    link,
                    fetch_page_metadata
                )
        except Exception as e:
            logger.warning(f"Failed to load connector '{modname}': {e}")
    if return_names_only:
        return sorted(names)
    return dict(dispatch)


def cli_main(ctx) -> None:
    """
    Main entry point for the RSS to Socials automation script.
    Validates environment, fetches new RSS entries, generates summaries, and posts to selected platforms.
    """
    feed_url = ctx.feed_url
    seen_file = ctx.seen_file
    post_age_limit_days = ctx.post_age_limit_days
    platforms = ctx.platforms
    if not feed_url:
        raise ValueError("FEED_URL must be provided via CLI or environment variable.")
    entries = fetch_rss_entries(feed_url)
    seen_links = load_seen_links(seen_file)
    now = datetime.now(timezone.utc)
    platform_dispatch = discover_platforms(return_names_only=False)
    if isinstance(platform_dispatch, list):
        platform_dispatch = {k: v for k, v in platform_dispatch}
    for entry in entries:
        link, pub_date = parse_entry_link_and_date(entry)
        is_new_link = link and link not in seen_links
        is_recent = pub_date and (now - pub_date) < timedelta(days=post_age_limit_days)
        logger.debug(f"Processing link: {link}, New: {is_new_link}, Recent: {is_recent}")
        if is_new_link and is_recent:
            try:
                posted = False
                for platform in set(platforms):
                    logger.debug(f"Posting to platform: {platform}")
                    handler = platform_dispatch.get(platform)
                    if handler:
                        result = handler(link)
                        posted = posted or result
                    else:
                        logger.warning(f"Platform '{platform}' is not supported.")
                if posted and isinstance(link, str):
                    seen_links.add(link)
                    save_seen_links(seen_links, seen_file)
            except Exception as e:
                logger.error(f"Error posting {link}: {e}")
        else:
            logger.info(f"Skipping already seen or old link: {link}")
