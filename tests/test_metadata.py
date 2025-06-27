from unittest.mock import patch
from rss2socials.common import metadata


# --- fetch_page_metadata ---
def test_fetch_page_metadata_none(monkeypatch):
    monkeypatch.setattr(metadata.trafilatura, 'fetch_url', lambda url: None)
    assert metadata.fetch_page_metadata('http://x') is None


def test_fetch_page_metadata_og_tags(monkeypatch):
    html_str = '''<html><head>
        <meta property="og:title" content="Test Title">
        <meta property="og:image" content="/img.png">
        <meta property="og:url" content="/page">
        <meta name="og:desc" content="desc">
        <meta property="notog" content="nope">
    </head></html>'''
    monkeypatch.setattr(metadata.trafilatura, 'fetch_url', lambda url: html_str)

    class FakeMeta:
        def __init__(self, attrib): self.attrib = attrib

    class FakeTree:
        def xpath(self, expr):
            return [
                FakeMeta({'property': 'og:title', 'content': 'Test Title'}),
                FakeMeta({'property': 'og:image', 'content': '/img.png'}),
                FakeMeta({'property': 'og:url', 'content': '/page'}),
                FakeMeta({'name': 'og:desc', 'content': 'desc'}),
                FakeMeta({'property': 'notog', 'content': 'nope'})
            ]
    monkeypatch.setattr(metadata.html, 'fromstring', lambda s: FakeTree())
    result = metadata.fetch_page_metadata('http://host/x')
    print("DEBUG result:", result)
    assert result is not None, "Result is None, see print above."
    assert result['og:title'] == 'Test Title'
    assert result['og:image'] == 'http://host/img.png'
    assert result['og:url'] == 'http://host/page'
    assert result['og:desc'] == 'desc'
    assert 'notog' not in result


def test_fetch_page_metadata_no_og(monkeypatch):
    html_str = '<html><head><meta property="notog" content="nope"></head></html>'
    monkeypatch.setattr(metadata.trafilatura, 'fetch_url', lambda url: html_str)

    class FakeMeta:
        def __init__(self, attrib): self.attrib = attrib

    class FakeTree:
        def xpath(self, expr): return [FakeMeta({'property': 'notog', 'content': 'nope'})]
    monkeypatch.setattr(metadata.html, 'fromstring', lambda s: FakeTree())
    assert metadata.fetch_page_metadata('http://host/x') is None


@patch('rss2socials.common.metadata.logging')
def test_fetch_page_metadata_exception(mock_logger, monkeypatch):
    monkeypatch.setattr(metadata.trafilatura, 'fetch_url', lambda url: '<html></html>')
    def raise_exc(s): raise ValueError('fail')
    monkeypatch.setattr(metadata.html, 'fromstring', raise_exc)
    assert metadata.fetch_page_metadata('http://host/x') is None
    assert any('Error parsing metadata' in str(call) for call in mock_logger.error.call_args_list)
