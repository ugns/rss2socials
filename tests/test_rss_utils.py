from rss2socials.common import rss_utils
import time


# --- fetch_rss_entries ---
def test_fetch_rss_entries(monkeypatch):
    class FakeFeed:
        entries = [{'title': 'Test'}]
    monkeypatch.setattr(rss_utils.feedparser, 'parse', lambda url: FakeFeed())
    entries = rss_utils.fetch_rss_entries('http://example.com/feed')
    assert entries == [{'title': 'Test'}]


# --- parse_entry_link_and_date ---
def test_parse_entry_link_and_date_published():
    entry = {
        "link": "http://example.com",
        "published_parsed": time.struct_time((2023, 1, 1, 0, 0, 0, 6, 1, -1))
    }
    link, pub_date = rss_utils.parse_entry_link_and_date(entry)
    assert link == "http://example.com"
    assert pub_date is not None and pub_date.year == 2023


def test_parse_entry_link_and_date_updated():
    entry = {
        "link": "http://example.com",
        "updated_parsed": time.struct_time((2022, 2, 2, 0, 0, 0, 2, 33, -1))
    }
    link, pub_date = rss_utils.parse_entry_link_and_date(entry)
    assert link == "http://example.com"
    assert pub_date is not None and pub_date.year == 2022


def test_parse_entry_link_and_date_none():
    entry = {"link": "http://example.com"}
    link, pub_date = rss_utils.parse_entry_link_and_date(entry)
    assert link == "http://example.com"
    assert pub_date is None


# --- load_seen_links ---
def test_load_seen_links(tmp_path):
    file = tmp_path / 'seen.txt'
    file.write_text('http://a.com\nhttp://b.com\n')
    seen = rss_utils.load_seen_links(str(file))
    assert 'http://a.com' in seen and 'http://b.com' in seen


def test_load_seen_links_missing():
    seen = rss_utils.load_seen_links('nonexistent.txt')
    assert seen == set()


# --- save_seen_links ---
def test_save_seen_links(tmp_path):
    file = tmp_path / 'seen.txt'
    links = {'http://a.com', 'http://b.com'}
    rss_utils.save_seen_links(links, str(file))
    content = file.read_text()
    assert 'http://a.com' in content and 'http://b.com' in content


def test_save_seen_links_handles_error(monkeypatch, caplog):
    def raise_ioerror(*a, **k):
        raise OSError('fail')
    monkeypatch.setattr('builtins.open', raise_ioerror)
    rss_utils.save_seen_links({'x'}, 'file.txt')
    assert any('Error saving seen links' in r for r in caplog.text.splitlines())


def test_load_seen_links_handles_error(monkeypatch, caplog):
    def raise_ioerror(*a, **k):
        raise OSError('fail')
    monkeypatch.setattr('builtins.open', raise_ioerror)
    # Create a dummy file so os.path.exists returns True
    monkeypatch.setattr('os.path.exists', lambda f: True)
    seen = rss_utils.load_seen_links('file.txt')
    assert seen == set()
    assert any('Error reading seen links' in r for r in caplog.text.splitlines())
