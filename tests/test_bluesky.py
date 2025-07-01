import pytest
from unittest.mock import patch, MagicMock
from rss2socials.connector import bluesky


# --- parse_hashtags_and_links ---
def test_parse_hashtags_and_links_tags_and_links():
    msg = "Check #hashtag and https://example.com"
    tb = bluesky.parse_hashtags_and_links(msg)
    # Should build text with tag and link
    built = tb.build_text()
    assert "#hashtag" in built
    assert "example.com" in built


def test_parse_hashtags_and_links_plain():
    msg = "Just plain text"
    tb = bluesky.parse_hashtags_and_links(msg)
    assert tb.build_text() == msg


# --- create_bluesky_embed (now a method) ---
@patch('atproto.models.AppBskyEmbedExternal.Main')
@patch('atproto.models.AppBskyEmbedExternal.External')
def test_create_bluesky_embed_with_image(mock_external, mock_main):
    meta = {'og:image': 'http://img', 'og:url': 'u', 'og:title': 't', 'og:description': 'd'}
    client = MagicMock()
    upload_result = MagicMock()
    upload_result.ref = 'ref'
    client.upload_blob.return_value = upload_result
    mock_external.return_value = MagicMock()
    mock_main.return_value = MagicMock(external=MagicMock(title='t'))
    with patch('requests.get') as mock_get:
        mock_resp = MagicMock()
        mock_resp.content = b'data'
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp
        bsky = bluesky.BlueskyClient.__new__(bluesky.BlueskyClient)
        bsky.client = client
        embed = bsky.create_bluesky_embed(meta)
    assert embed is not None
    assert embed.external.title == 't'


@patch('atproto.models.AppBskyEmbedExternal.Main')
@patch('atproto.models.AppBskyEmbedExternal.External')
def test_create_bluesky_embed_no_image(mock_external, mock_main):
    meta = {'og:url': 'u', 'og:title': 't', 'og:description': 'd'}
    client = MagicMock()
    mock_external.return_value = MagicMock()
    mock_main.return_value = MagicMock(external=MagicMock(title='t'))
    bsky = bluesky.BlueskyClient.__new__(bluesky.BlueskyClient)
    bsky.client = client
    embed = bsky.create_bluesky_embed(meta)
    assert embed is not None
    assert embed.external.title == 't'


@patch('atproto.models.AppBskyEmbedExternal.Main')
@patch('atproto.models.AppBskyEmbedExternal.External')
def test_create_bluesky_embed_image_error(mock_external, mock_main):
    meta = {'og:image': 'http://img', 'og:url': 'u', 'og:title': 't', 'og:description': 'd'}
    client = MagicMock()
    mock_external.return_value = MagicMock()
    mock_main.return_value = MagicMock(external=MagicMock(title='t'))
    with patch('requests.get', side_effect=Exception('fail')):
        bsky = bluesky.BlueskyClient.__new__(bluesky.BlueskyClient)
        bsky.client = client
        embed = bsky.create_bluesky_embed(meta)
    assert embed is not None


@patch('atproto.models.AppBskyEmbedExternal.Main', side_effect=Exception('fail'))
def test_create_bluesky_embed_embed_error(mock_main):
    meta = {'og:url': 'u', 'og:title': 't', 'og:description': 'd'}
    client = MagicMock()
    bsky = bluesky.BlueskyClient.__new__(bluesky.BlueskyClient)
    bsky.client = client
    embed = bsky.create_bluesky_embed(meta)
    assert embed is None


@patch('atproto.models.AppBskyEmbedExternal.Main')
@patch('atproto.models.AppBskyEmbedExternal.External')
def test_create_bluesky_embed_upload_blob_error(mock_external, mock_main):
    meta = {'og:image': 'http://img', 'og:url': 'u', 'og:title': 't', 'og:description': 'd'}
    client = MagicMock()
    client.upload_blob.side_effect = Exception('blob fail')
    mock_external.return_value = MagicMock()
    mock_main.return_value = MagicMock(external=MagicMock(title='t'))
    with patch('requests.get') as mock_get:
        mock_resp = MagicMock()
        mock_resp.content = b'data'
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp
        bsky = bluesky.BlueskyClient.__new__(bluesky.BlueskyClient)
        bsky.client = client
        embed = bsky.create_bluesky_embed(meta)
    assert embed is not None


@patch('atproto.models.AppBskyEmbedExternal.Main')
@patch('atproto.models.AppBskyEmbedExternal.External')
def test_create_bluesky_embed_upload_blob_no_ref_no_blob(mock_external, mock_main):
    meta = {'og:image': 'http://img', 'og:url': 'u', 'og:title': 't', 'og:description': 'd'}
    client = MagicMock()

    class NoRefNoBlob:  # This mock has neither 'ref' nor 'blob'
        pass
    upload_result = NoRefNoBlob()
    client.upload_blob.return_value = upload_result
    mock_external.return_value = MagicMock()
    mock_main.return_value = MagicMock(external=MagicMock(title='t'))
    with patch('requests.get') as mock_get:
        mock_resp = MagicMock()
        mock_resp.content = b'data'
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp
        bsky = bluesky.BlueskyClient.__new__(bluesky.BlueskyClient)
        bsky.client = client
        embed = bsky.create_bluesky_embed(meta)
    assert embed is not None
    assert embed.external.title == 't'


@patch('atproto.models.AppBskyEmbedExternal.Main')
@patch('atproto.models.AppBskyEmbedExternal.External')
def test_create_bluesky_embed_upload_blob_blob_attr(mock_external, mock_main):
    meta = {'og:image': 'http://img', 'og:url': 'u', 'og:title': 't', 'og:description': 'd'}
    client = MagicMock()

    class BlobOnly:  # This mock has a 'blob' attribute but no 'ref'
        blob = 'blob-value'
    upload_result = BlobOnly()
    client.upload_blob.return_value = upload_result
    mock_external.return_value = MagicMock()
    mock_main.return_value = MagicMock(external=MagicMock(title='t'))
    with patch('requests.get') as mock_get:
        mock_resp = MagicMock()
        mock_resp.content = b'data'
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp
        bsky = bluesky.BlueskyClient.__new__(bluesky.BlueskyClient)
        bsky.client = client
        embed = bsky.create_bluesky_embed(meta)
    assert embed is not None
    assert embed.external.title == 't'


# --- post ---
# Success cases
@patch('atproto.models.AppBskyEmbedExternal.Main')
@patch('atproto.models.AppBskyEmbedExternal.External')
@patch('rss2socials.connector.bluesky.Client')
@patch('rss2socials.connector.bluesky.DidInMemoryCache')
@patch('rss2socials.connector.bluesky.IdResolver')
def test_post_success(mock_resolver, mock_cache, mock_client, mock_external, mock_main, monkeypatch):
    monkeypatch.setenv('BLUESKY_HANDLE', 'h')
    monkeypatch.setenv('BLUESKY_APP_PASSWORD', 'p')
    resolver = MagicMock()
    resolver.handle.resolve.return_value = 'resolved'
    did = MagicMock()
    did.get_pds_endpoint.return_value = 'url'
    resolver.did.resolve.return_value = did
    mock_resolver.return_value = resolver
    client = MagicMock()
    mock_client.return_value = client
    mock_external.return_value = MagicMock()
    mock_main.return_value = MagicMock(external=MagicMock(title='t'))

    def fetch_meta(link):
        return {'og:title': 't'}
    # Reset singleton for isolation
    bluesky._bluesky_client = None
    result = bluesky.post('msg #tag http://x', 'http://x', fetch_meta)
    assert result is True
    assert client.login.called
    assert client.send_post.called


@patch('atproto.models.AppBskyEmbedExternal.Main')
@patch('atproto.models.AppBskyEmbedExternal.External')
@patch('rss2socials.connector.bluesky.Client')
@patch('rss2socials.connector.bluesky.DidInMemoryCache')
@patch('rss2socials.connector.bluesky.IdResolver')
def test_post_success_no_embed(mock_resolver, mock_cache, mock_client, mock_external, mock_main, monkeypatch):
    monkeypatch.setenv('BLUESKY_HANDLE', 'h')
    monkeypatch.setenv('BLUESKY_APP_PASSWORD', 'p')
    resolver = MagicMock()
    resolver.handle.resolve.return_value = 'resolved'
    did = MagicMock()
    did.get_pds_endpoint.return_value = 'url'
    resolver.did.resolve.return_value = did
    mock_resolver.return_value = resolver
    client = MagicMock()
    mock_client.return_value = client
    mock_external.return_value = MagicMock()
    mock_main.return_value = MagicMock(external=MagicMock(title='t'))

    def fetch_meta(link):
        return {'og:title': 't'}
    # Patch BlueskyClient.create_bluesky_embed to return None
    with patch.object(bluesky.BlueskyClient, 'create_bluesky_embed', return_value=None):
        bluesky._bluesky_client = None
        result = bluesky.post('msg #tag http://x', 'http://x', fetch_meta)
    assert result is True
    assert client.login.called
    assert client.send_post.called


@patch('atproto.models.AppBskyEmbedExternal.Main')
@patch('atproto.models.AppBskyEmbedExternal.External')
@patch('rss2socials.connector.bluesky.Client')
@patch('rss2socials.connector.bluesky.DidInMemoryCache')
@patch('rss2socials.connector.bluesky.IdResolver')
def test_post_resolve_did_none(mock_resolver, mock_cache, mock_client, mock_external, mock_main, monkeypatch):
    monkeypatch.setenv('BLUESKY_HANDLE', 'h')
    monkeypatch.setenv('BLUESKY_APP_PASSWORD', 'p')
    resolver = MagicMock()
    resolver.handle.resolve.return_value = 'resolved'
    resolver.did.resolve.return_value = None
    mock_resolver.return_value = resolver
    client = MagicMock()
    mock_client.return_value = client
    mock_external.return_value = MagicMock()
    mock_main.return_value = MagicMock(external=MagicMock(title='t'))
    bluesky._bluesky_client = None
    result = bluesky.post('msg', 'link', lambda x: {})
    assert result is True
    assert client.login.called
    assert client.send_post.called


# Error/edge cases
@patch('rss2socials.connector.bluesky.Client')
@patch('rss2socials.connector.bluesky.DidInMemoryCache')
@patch('rss2socials.connector.bluesky.IdResolver')
def test_post_no_handle(mock_resolver, mock_cache, mock_client, monkeypatch):
    monkeypatch.setenv('BLUESKY_APP_PASSWORD', 'p')
    monkeypatch.delenv('BLUESKY_HANDLE', raising=False)
    bluesky._bluesky_client = None
    with pytest.raises(ValueError):
        bluesky.post('msg', 'link', lambda x: {})


@patch('rss2socials.connector.bluesky.Client')
@patch('rss2socials.connector.bluesky.DidInMemoryCache')
@patch('rss2socials.connector.bluesky.IdResolver')
def test_post_resolve_handle_none(mock_resolver, mock_cache, mock_client, monkeypatch):
    monkeypatch.setenv('BLUESKY_HANDLE', 'h')
    monkeypatch.setenv('BLUESKY_APP_PASSWORD', 'p')
    resolver = MagicMock()
    resolver.handle.resolve.return_value = None
    mock_resolver.return_value = resolver
    bluesky._bluesky_client = None
    with pytest.raises(ValueError):
        bluesky.post('msg', 'link', lambda x: {})


@patch('atproto.models.AppBskyEmbedExternal.Main')
@patch('atproto.models.AppBskyEmbedExternal.External')
@patch('rss2socials.connector.bluesky.Client')
@patch('rss2socials.connector.bluesky.DidInMemoryCache')
@patch('rss2socials.connector.bluesky.IdResolver')
def test_post_login_error(mock_resolver, mock_cache, mock_client, mock_external, mock_main, monkeypatch):
    monkeypatch.setenv('BLUESKY_HANDLE', 'h')
    monkeypatch.setenv('BLUESKY_APP_PASSWORD', 'p')
    resolver = MagicMock()
    resolver.handle.resolve.return_value = 'resolved'
    did = MagicMock()
    did.get_pds_endpoint.return_value = 'url'
    resolver.did.resolve.return_value = did
    mock_resolver.return_value = resolver
    client = MagicMock()
    client.login.side_effect = Exception('fail')
    mock_client.return_value = client
    mock_external.return_value = MagicMock()
    mock_main.return_value = MagicMock(external=MagicMock(title='t'))
    bluesky._bluesky_client = None
    with pytest.raises(Exception):
        bluesky.post('msg', 'link', lambda x: {})


@patch('atproto.models.AppBskyEmbedExternal.Main')
@patch('atproto.models.AppBskyEmbedExternal.External')
@patch('rss2socials.connector.bluesky.Client')
@patch('rss2socials.connector.bluesky.DidInMemoryCache')
@patch('rss2socials.connector.bluesky.IdResolver')
def test_post_send_post_error(mock_resolver, mock_cache, mock_client, mock_external, mock_main, monkeypatch):
    monkeypatch.setenv('BLUESKY_HANDLE', 'h')
    monkeypatch.setenv('BLUESKY_APP_PASSWORD', 'p')
    resolver = MagicMock()
    resolver.handle.resolve.return_value = 'resolved'
    did = MagicMock()
    did.get_pds_endpoint.return_value = 'url'
    resolver.did.resolve.return_value = did
    mock_resolver.return_value = resolver
    client = MagicMock()
    client.send_post.side_effect = Exception('fail')
    mock_client.return_value = client
    mock_external.return_value = MagicMock()
    mock_main.return_value = MagicMock(external=MagicMock(title='t'))
    bluesky._bluesky_client = None
    with pytest.raises(Exception):
        bluesky.post('msg', 'link', lambda x: {})


@patch('atproto.models.AppBskyEmbedExternal.Main')
@patch('atproto.models.AppBskyEmbedExternal.External')
@patch('rss2socials.connector.bluesky.Client')
@patch('rss2socials.connector.bluesky.DidInMemoryCache')
@patch('rss2socials.connector.bluesky.IdResolver')
def test_post_unexpected_error(mock_resolver, mock_cache, mock_client, mock_external, mock_main, monkeypatch):
    monkeypatch.setenv('BLUESKY_HANDLE', 'h')
    monkeypatch.setenv('BLUESKY_APP_PASSWORD', 'p')
    resolver = MagicMock()
    resolver.handle.resolve.return_value = 'resolved'
    did = MagicMock()
    did.get_pds_endpoint.return_value = 'url'
    resolver.did.resolve.return_value = did
    mock_resolver.return_value = resolver
    client = MagicMock()
    # login works, but parse_hashtags_and_links will raise
    mock_client.return_value = client
    mock_external.return_value = MagicMock()
    mock_main.return_value = MagicMock(external=MagicMock(title='t'))
    bluesky._bluesky_client = None
    with patch('rss2socials.connector.bluesky.parse_hashtags_and_links', side_effect=Exception('fail-parse')):
        with pytest.raises(Exception) as excinfo:
            bluesky.post('msg', 'link', lambda x: {})
        assert 'fail-parse' in str(excinfo.value)


@patch('rss2socials.connector.bluesky.Client')
@patch('rss2socials.connector.bluesky.DidInMemoryCache')
@patch('rss2socials.connector.bluesky.IdResolver')
def test_post_login_atprotoerror(mock_resolver, mock_cache, mock_client, monkeypatch, caplog):
    monkeypatch.setenv('BLUESKY_HANDLE', 'h')
    monkeypatch.setenv('BLUESKY_APP_PASSWORD', 'p')
    resolver = MagicMock()
    resolver.handle.resolve.return_value = 'resolved'
    did = MagicMock()
    did.get_pds_endpoint.return_value = 'url'
    resolver.did.resolve.return_value = did
    mock_resolver.return_value = resolver

    # Dynamically create a fake AtProtocolError
    class AtProtocolError(Exception):
        pass
    client = MagicMock()
    client.login.side_effect = AtProtocolError('fail')
    mock_client.return_value = client
    # Patch atproto.exceptions.AtProtocolError in the module under test
    with patch('atproto.exceptions.AtProtocolError', AtProtocolError):
        with pytest.raises(Exception):
            bluesky._bluesky_client = None
            bluesky.post('msg', 'link', lambda x: {})
    assert any('AtProtocolError during login' in r for r in caplog.text.splitlines())
