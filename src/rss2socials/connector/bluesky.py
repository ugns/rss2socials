import os
import requests
from atproto import Client, DidInMemoryCache, IdResolver, client_utils, models
from urllib.parse import urlparse
from typing import Any, Callable, Optional
import logging

__all__ = [
    "post",
    "MAX_GRAPHEMES",
]

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


def create_bluesky_embed(meta: Optional[dict], client: Any) -> Optional[Any]:
    """
    Create a Bluesky external embed with optional image blob.

    Args:
        meta: Open Graph metadata dictionary.
        client: The Bluesky client instance.

    Returns:
        An embed object or None if creation fails.
    """
    thumb_blob = None
    if meta and 'og:image' in meta:
        try:
            img_resp = requests.get(meta['og:image'], timeout=10)
            img_resp.raise_for_status()
            upload_result = client.upload_blob(img_resp.content)
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
        embed = models.AppBskyEmbedExternal.Main(
            external=models.AppBskyEmbedExternal.External(
                uri=meta['og:url'] if meta and 'og:url' in meta else "",
                title=meta['og:title'] if meta and 'og:title' in meta else "",
                description=meta['og:description'] if meta and 'og:description' in meta else "",
                thumb=thumb_blob if (thumb_blob is not None and hasattr(
                    thumb_blob, 'ref')) else None
            )
        )
    except Exception as embed_err:
        logging.error(f"[Bluesky] Error creating embed: {embed_err}")
        embed = None
    return embed


def post(
    message: str,
    link: str,
    fetch_page_metadata: Callable[[str], Optional[dict]]
) -> None:
    """
    Post a message to Bluesky, including a social card embed if available.

    Args:
        message: The post content.
        link: The URL to include in the post.
        fetch_page_metadata: Function to fetch Open Graph metadata for the link.

    Raises:
        EnvironmentError: If required Bluesky environment variables are missing.
        Exception: For errors during posting.
    """
    try:
        handle = os.getenv("BLUESKY_HANDLE")
        app_password = os.getenv("BLUESKY_APP_PASSWORD")
        cache = DidInMemoryCache()
        resolver = IdResolver(cache=cache)
        # The following check is now redundant, but left for extra safety
        if handle is None:
            raise ValueError("BLUESKY_HANDLE environment variable is not set.")
        resolved_handle = resolver.handle.resolve(handle)
        if resolved_handle is None:
            raise ValueError(f"Could not resolve handle: {handle}")
        did = resolver.did.resolve(resolved_handle)
        if did is not None and hasattr(did, "get_pds_endpoint") and did.get_pds_endpoint():
            client = Client(base_url=did.get_pds_endpoint())
        else:
            client = Client()
        client.login(handle, app_password)
        tb = parse_hashtags_and_links(message)
        meta = fetch_page_metadata(link)
        embed = create_bluesky_embed(meta, client)
        if embed:
            client.send_post(tb, embed=embed)
        else:
            client.send_post(tb)
        logging.info(f"[Bluesky] Posted: {tb.build_text()}")
    except Exception as e:
        logging.error(f"[Bluesky] Error posting to Bluesky: {e}")
        raise
