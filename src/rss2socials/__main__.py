import os
from dotenv import load_dotenv
import argparse
from . import __version__
from .cli import cli_main, discover_platforms
import logging
from dataclasses import dataclass

# Load environment variables from .env file automatically
load_dotenv()


def get_version() -> str:
    pkg_dir = os.path.join(os.path.dirname(__file__))
    pkg_dir = os.path.abspath(pkg_dir)

    return f"%(prog)s {__version__} from {pkg_dir}"


def create_parser():
    available_platforms = discover_platforms(return_names_only=True)
    parser = argparse.ArgumentParser(
        description="Post new RSS feed entries to supported platforms.")
    parser.add_argument('--feed-url', default=os.getenv("FEED_URL"),
                        required=True, help="RSS/Atom feed URL (or set FEED_URL env var)")
    parser.add_argument('--seen-file', default=os.getenv("SEEN_FILE",
                        "seen_rss_posts.txt"), help="File to track seen links")
    parser.add_argument('--post-age-limit-days', type=int, default=int(
        os.getenv("POST_AGE_LIMIT_DAYS", "7")), help="Max age in days for posts")
    parser.add_argument('--log-level', default=os.getenv("LOG_LEVEL", "INFO"),
                        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                        help="Set the logging level (default: INFO)")
    parser.add_argument('--version', action='version', version=get_version())
    platform_env = os.getenv("PLATFORM")
    if platform_env:
        platform_default = [p.strip() for p in platform_env.split(',') if p.strip() in available_platforms]
        if not platform_default:
            platform_default = ["bluesky"]
    else:
        platform_default = ["bluesky"]
    parser.add_argument('--platform', nargs='+', default=platform_default,
                        choices=available_platforms,
                        help=f"Platform(s) to post to (default: bluesky). Available: {', '.join(available_platforms)}")
    return parser


@dataclass
class CliContext:
    feed_url: str
    seen_file: str
    post_age_limit_days: int
    platforms: list
    log_level: str


def main():
    parser = create_parser()
    args = parser.parse_args()
    # Configure logging level
    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO), format='[%(levelname)s] %(message)s')
    ctx = CliContext(
        feed_url=args.feed_url,
        seen_file=args.seen_file,
        post_age_limit_days=args.post_age_limit_days,
        platforms=args.platform,
        log_level=args.log_level,
    )
    try:
        logging.info(f"Starting rss2socials version {__version__}")
        logging.debug(f"Args: {ctx}")
        cli_main(ctx)
    except Exception as e:
        logging.error(f"Error: {e}")


if __name__ == "__main__":
    main()
