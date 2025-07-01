import os
from atproto import Client, DidInMemoryCache, IdResolver, client_utils
from urllib.parse import urlparse
from typing import Any, Callable, Optional
import logging

__all__ = [
    "post",
    "MAX_GRAPHEMES",
]

PLATFORM = "bluesky"
# Maximum graphemes for a post, as per Bluesky's API limits.
# This is set to 300, which is the maximum allowed by the API.
MAX_GRAPHEMES = 300


def parse_hashtags_and_links(message: str) -> Any:
    """
    Build a TextBuilder object, tagging hashtags and linking URLs in the message.

    Args:
        message: The message string to parse.

    Returns:
        A TextBuilder object with hashtags and links tagged.
    """
    import re
    tb = client_utils.TextBuilder()
    last_idx = 0
    for match in re.finditer(r"#\w+|https?://[\w\.-]+(?:/[\w\./?%&=\-]*)?", message):
        start, end = match.span()
        if start > last_idx:
            tb.text(message[last_idx:start])
        token = message[start:end]
        if token.startswith('#'):
            tb.tag(token, token.lstrip('#'))
        elif token.startswith('http'):
            hostname = urlparse(token).hostname or token
            tb.link(hostname, token)
        last_idx = end
    if last_idx < len(message):
        tb.text(message[last_idx:])
    return tb


class BlueskyClient:
    """
    Authenticated Bluesky client for posting messages with optional embeds.

    Handles authentication and connection setup once per process.
    Use the `post` method to send posts with optional Open Graph metadata.
    """
    def __init__(self):
        """
        Initialize and authenticate the Bluesky client using environment variables.

        Raises:
            ValueError: If required environment variables are missing or handle cannot be resolved.
        """
        self.client: Client
        handle = os.getenv("BLUESKY_HANDLE")
        app_password = os.getenv("BLUESKY_APP_PASSWORD")
        cache = DidInMemoryCache()
        resolver = IdResolver(cache=cache)
        if handle is None:
            raise ValueError("BLUESKY_HANDLE environment variable is not set.")
        resolved_handle = resolver.handle.resolve(handle)
        if resolved_handle is None:
            raise ValueError(f"Could not resolve handle: {handle}")
        did = resolver.did.resolve(resolved_handle)
        if did is not None and hasattr(did, "get_pds_endpoint") and did.get_pds_endpoint():
            self.client = Client(base_url=did.get_pds_endpoint())
        else:
            self.client = Client()
        try:
            self.client.login(handle, app_password)
        except Exception as e:
            from atproto.exceptions import AtProtocolError
            if isinstance(e, AtProtocolError):
                logging.error(f"[Bluesky] AtProtocolError during login: {e}")
                raise
            else:
                raise

    def create_bluesky_embed(self, meta: Optional[dict]) -> Optional[Any]:
        """
        Create a Bluesky external embed with optional image blob.

        Args:
            meta: Open Graph metadata dictionary.

        Returns:
            An embed object or None if creation fails.
        """
        thumb_blob = None
        if meta and 'og:image' in meta:
            try:
                import requests
                img_resp = requests.get(meta['og:image'], timeout=10)
                img_resp.raise_for_status()
                upload_result = self.client.upload_blob(img_resp.content)
                if hasattr(upload_result, 'ref') and 'Response' not in str(type(upload_result)):
                    thumb_blob = upload_result
                elif hasattr(upload_result, 'blob'):
                    thumb_blob = upload_result.blob
                else:
                    thumb_blob = None
            except Exception as img_err:
                logging.error(f"[Bluesky] Error uploading image blob: {img_err}")
                thumb_blob = None
        try:
            from atproto import models
            thumb = None  # type: Optional[Any]
            if thumb_blob is not None and hasattr(thumb_blob, 'ref'):
                thumb = thumb_blob
            embed = models.AppBskyEmbedExternal.Main(
                external=models.AppBskyEmbedExternal.External(
                    uri=meta['og:url'] if meta and 'og:url' in meta else "",
                    title=meta['og:title'] if meta and 'og:title' in meta else "",
                    description=meta['og:description'] if meta and 'og:description' in meta else "",
                    thumb=thumb
                )
            )
        except Exception as embed_err:
            logging.error(f"[Bluesky] Error creating embed: {embed_err}")
            embed = None
        return embed

    def post(self, message: str, link: str, fetch_page_metadata: Callable[[str], Optional[dict]]) -> None:
        """
        Post a message to Bluesky, including a social card embed if available.

        Args:
            message: The post content.
            link: The URL to include in the post.
            fetch_page_metadata: Function to fetch Open Graph metadata for the link.
        """
        tb = parse_hashtags_and_links(message)
        logging.debug(f"[Bluesky] Posting message: {tb.build_text()} with link: {link}")
        meta = fetch_page_metadata(link)
        embed = self.create_bluesky_embed(meta)
        if embed:
            self.client.send_post(tb, embed=embed)
        else:
            self.client.send_post(tb)
        logging.info(f"[Bluesky] Posted: {tb.build_text()}")


# Singleton instance for module-level post function
_bluesky_client: Optional[BlueskyClient] = None


def post(
    message: str,
    link: str,
    fetch_page_metadata: Callable[[str], Optional[dict]]
) -> bool:
    """
    Post a message to Bluesky, including a social card embed if available.

    This function uses a singleton BlueskyClient instance to avoid re-authenticating
    for every post. It is the main entry point for posting to Bluesky from this module.

    Args:
        message: The post content.
        link: The URL to include in the post.
        fetch_page_metadata: Function to fetch Open Graph metadata for the link.

    Raises:
        Exception: For errors during posting.
    """
    global _bluesky_client
    if _bluesky_client is None:
        _bluesky_client = BlueskyClient()
    try:
        _bluesky_client.post(message, link, fetch_page_metadata)
        return True
    except Exception as e:
        logging.error(f"[Bluesky] Error posting to Bluesky: {e}")
        raise
