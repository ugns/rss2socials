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


# --- create_bluesky_embed ---
@patch('rss2socials.connector.bluesky.models.AppBskyEmbedExternal.Main')
@patch('rss2socials.connector.bluesky.models.AppBskyEmbedExternal.External')
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
        embed = bluesky.create_bluesky_embed(meta, client)
    assert embed is not None
    assert embed.external.title == 't'


@patch('rss2socials.connector.bluesky.models.AppBskyEmbedExternal.Main')
@patch('rss2socials.connector.bluesky.models.AppBskyEmbedExternal.External')
def test_create_bluesky_embed_no_image(mock_external, mock_main):
    meta = {'og:url': 'u', 'og:title': 't', 'og:description': 'd'}
    client = MagicMock()
    mock_external.return_value = MagicMock()
    mock_main.return_value = MagicMock(external=MagicMock(title='t'))
    embed = bluesky.create_bluesky_embed(meta, client)
    assert embed is not None
    assert embed.external.title == 't'


@patch('rss2socials.connector.bluesky.models.AppBskyEmbedExternal.Main')
@patch('rss2socials.connector.bluesky.models.AppBskyEmbedExternal.External')
def test_create_bluesky_embed_image_error(mock_external, mock_main):
    meta = {'og:image': 'http://img', 'og:url': 'u', 'og:title': 't', 'og:description': 'd'}
    client = MagicMock()
    mock_external.return_value = MagicMock()
    mock_main.return_value = MagicMock(external=MagicMock(title='t'))
    with patch('requests.get', side_effect=Exception('fail')):
        embed = bluesky.create_bluesky_embed(meta, client)
    assert embed is not None


@patch('rss2socials.connector.bluesky.models.AppBskyEmbedExternal.Main', side_effect=Exception('fail'))
def test_create_bluesky_embed_embed_error(mock_main):
    meta = {'og:url': 'u', 'og:title': 't', 'og:description': 'd'}
    client = MagicMock()
    embed = bluesky.create_bluesky_embed(meta, client)
    assert embed is None


@patch('rss2socials.connector.bluesky.models.AppBskyEmbedExternal.Main')
@patch('rss2socials.connector.bluesky.models.AppBskyEmbedExternal.External')
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
        embed = bluesky.create_bluesky_embed(meta, client)
    assert embed is not None


@patch('rss2socials.connector.bluesky.models.AppBskyEmbedExternal.Main')
@patch('rss2socials.connector.bluesky.models.AppBskyEmbedExternal.External')
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
        embed = bluesky.create_bluesky_embed(meta, client)
    assert embed is not None
    assert embed.external.title == 't'


@patch('rss2socials.connector.bluesky.models.AppBskyEmbedExternal.Main')
@patch('rss2socials.connector.bluesky.models.AppBskyEmbedExternal.External')
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
        embed = bluesky.create_bluesky_embed(meta, client)
    assert embed is not None
    assert embed.external.title == 't'


# --- post ---
# Success cases
@patch('rss2socials.connector.bluesky.models.AppBskyEmbedExternal.Main')
@patch('rss2socials.connector.bluesky.models.AppBskyEmbedExternal.External')
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
    bluesky.post('msg #tag http://x', 'http://x', fetch_meta)
    assert client.login.called
    assert client.send_post.called


@patch('rss2socials.connector.bluesky.models.AppBskyEmbedExternal.Main')
@patch('rss2socials.connector.bluesky.models.AppBskyEmbedExternal.External')
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
    # Patch create_bluesky_embed to return None
    with patch('rss2socials.connector.bluesky.create_bluesky_embed', return_value=None):
        bluesky.post('msg #tag http://x', 'http://x', fetch_meta)
    assert client.login.called
    assert client.send_post.called


@patch('rss2socials.connector.bluesky.models.AppBskyEmbedExternal.Main')
@patch('rss2socials.connector.bluesky.models.AppBskyEmbedExternal.External')
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
    bluesky.post('msg', 'link', lambda x: {})
    assert client.login.called
    assert client.send_post.called


# Error/edge cases
@patch('rss2socials.connector.bluesky.Client')
@patch('rss2socials.connector.bluesky.DidInMemoryCache')
@patch('rss2socials.connector.bluesky.IdResolver')
def test_post_no_handle(mock_resolver, mock_cache, mock_client, monkeypatch):
    monkeypatch.setenv('BLUESKY_APP_PASSWORD', 'p')
    monkeypatch.delenv('BLUESKY_HANDLE', raising=False)
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
    with pytest.raises(ValueError):
        bluesky.post('msg', 'link', lambda x: {})


@patch('rss2socials.connector.bluesky.models.AppBskyEmbedExternal.Main')
@patch('rss2socials.connector.bluesky.models.AppBskyEmbedExternal.External')
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
    with pytest.raises(Exception):
        bluesky.post('msg', 'link', lambda x: {})


@patch('rss2socials.connector.bluesky.models.AppBskyEmbedExternal.Main')
@patch('rss2socials.connector.bluesky.models.AppBskyEmbedExternal.External')
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
    with pytest.raises(Exception):
        bluesky.post('msg', 'link', lambda x: {})


@patch('rss2socials.connector.bluesky.models.AppBskyEmbedExternal.Main')
@patch('rss2socials.connector.bluesky.models.AppBskyEmbedExternal.External')
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
    with patch('rss2socials.connector.bluesky.parse_hashtags_and_links', side_effect=Exception('fail-parse')):
        with pytest.raises(Exception) as excinfo:
            bluesky.post('msg', 'link', lambda x: {})
        assert 'fail-parse' in str(excinfo.value)
