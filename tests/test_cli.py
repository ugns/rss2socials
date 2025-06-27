import pytest
from unittest.mock import patch, MagicMock
from types import SimpleNamespace
from rss2socials.cli import cli_main, discover_platforms
from datetime import datetime, timezone


# --- Fixtures ---
@pytest.fixture
def fake_ctx():
    return SimpleNamespace(
        feed_url='http://example.com/feed',
        seen_file=':memory:',
        post_age_limit_days=7,
        platforms=['bluesky'],
        log_level='INFO',
    )


# --- discover_platforms ---
def test_discover_platforms_returns_dict():
    dispatch = discover_platforms()
    assert isinstance(dispatch, dict)
    assert 'bluesky' in dispatch
    assert callable(dispatch['bluesky'])


def test_discover_platforms_names():
    names = discover_platforms(return_names_only=True)
    assert isinstance(names, list)
    assert 'bluesky' in names


@patch('rss2socials.cli.logger')
def test_discover_platforms_import_exception(mock_logger, monkeypatch):
    from rss2socials import cli

    class DummyModule:
        __path__ = ['dummy']
    monkeypatch.setattr('rss2socials.cli.connector', DummyModule, raising=False)
    monkeypatch.setattr('pkgutil.iter_modules', lambda path: [(None, 'badmod', False)])
    monkeypatch.setattr('importlib.import_module', lambda *a, **k: (_ for _ in ()).throw(ImportError('fail')))
    names = cli.discover_platforms(return_names_only=True)
    assert 'badmod' not in names
    assert any('Failed to load connector' in str(call) for call in mock_logger.warning.call_args_list)


@patch('rss2socials.cli.logger')
def test_discover_platforms_skips_underscore_and_pkg(mock_logger, monkeypatch):
    from rss2socials import cli

    class DummyModule:
        __path__ = ['dummy']
    monkeypatch.setattr('rss2socials.cli.connector', DummyModule, raising=False)
    monkeypatch.setattr('pkgutil.iter_modules', lambda path: [
        (None, '_hidden', False),
        (None, 'realmod', True),  # ispkg=True
        (None, 'goodmod', False)
    ])

    def fake_import(name, *a, **k):
        class Mod:
            PLATFORM = 'goodmod'
            def post(*a, **k): return True
        if 'goodmod' in name:
            return Mod
    monkeypatch.setattr('importlib.import_module', fake_import)
    names = cli.discover_platforms(return_names_only=True)
    assert 'goodmod' in names
    assert '_hidden' not in names
    assert 'realmod' not in names  # ispkg=True should be skipped


# --- cli_main ---
@patch('rss2socials.cli.fetch_rss_entries')
@patch('rss2socials.cli.load_seen_links')
@patch('rss2socials.cli.parse_entry_link_and_date')
@patch('rss2socials.cli.save_seen_links')
@patch('rss2socials.cli.discover_platforms')
def test_cli_main_posts_to_platforms(mock_discover, mock_save, mock_parse, mock_load, mock_fetch, fake_ctx):
    mock_fetch.return_value = [{'id': 1}]
    mock_load.return_value = set()
    mock_parse.return_value = ('http://example.com/post', datetime.now(timezone.utc))
    fake_handler = MagicMock(return_value=True)
    mock_discover.return_value = {'bluesky': fake_handler}
    cli_main(fake_ctx)
    fake_handler.assert_called_once_with('http://example.com/post')


@patch('rss2socials.cli.logger')
@patch('rss2socials.cli.discover_platforms', return_value={})
@patch('rss2socials.cli.fetch_rss_entries')
@patch('rss2socials.cli.load_seen_links')
@patch('rss2socials.cli.parse_entry_link_and_date')
def test_cli_main_handles_unsupported_platform(mock_parse, mock_load, mock_fetch, mock_discover, mock_logger, fake_ctx):
    # Make sure the entry is new and recent
    mock_fetch.return_value = [{'id': 1}]
    mock_load.return_value = set()
    mock_parse.return_value = ('http://example.com/post', datetime.now(timezone.utc))
    fake_ctx.platforms = ['notareal']
    from rss2socials import cli
    cli.cli_main(fake_ctx)
    assert any("notareal" in str(call) for call in mock_logger.warning.call_args_list)


@patch('rss2socials.cli.logger')
@patch('rss2socials.cli.discover_platforms')
@patch('rss2socials.cli.fetch_rss_entries')
@patch('rss2socials.cli.load_seen_links')
@patch('rss2socials.cli.parse_entry_link_and_date')
def test_cli_main_exception_handling(mock_parse, mock_load, mock_fetch, mock_discover, mock_logger, fake_ctx):
    # Setup mocks to ensure is_new_link and is_recent are True
    mock_fetch.return_value = [{'id': 1}]
    mock_load.return_value = set()
    mock_parse.return_value = ('http://example.com/post', datetime.now(timezone.utc))
    # Handler that raises an exception

    def raise_exception(link):
        raise RuntimeError("Test exception")
    mock_discover.return_value = {'bluesky': raise_exception}
    fake_ctx.platforms = ['bluesky']
    from rss2socials import cli
    cli.cli_main(fake_ctx)
    assert any("Error posting" in str(call) and "Test exception" in str(call) for call in mock_logger.error.call_args_list)


@patch('rss2socials.cli.logger')
def test_cli_main_platform_dispatch_list(mock_logger, fake_ctx):
    # Simulate discover_platforms returning a list of tuples
    from rss2socials import cli
    handler = MagicMock(return_value=True)
    fake_ctx.platforms = ['bluesky']
    # Patch discover_platforms in the cli module's namespace
    with patch.object(cli, 'discover_platforms', return_value=[('bluesky', handler)]):
        with patch('rss2socials.cli.fetch_rss_entries', return_value=[{'id': 1}]):
            with patch('rss2socials.cli.load_seen_links', return_value=set()):
                with patch('rss2socials.cli.parse_entry_link_and_date',
                           return_value=('http://example.com/post', datetime.now(timezone.utc))):
                    with patch('rss2socials.cli.save_seen_links'):
                        cli.cli_main(fake_ctx)
    handler.assert_called_once_with('http://example.com/post')


@patch('rss2socials.cli.logger')
def test_cli_main_skips_seen_or_old_link(mock_logger, fake_ctx):
    from rss2socials import cli
    with patch('rss2socials.cli.fetch_rss_entries', return_value=[{'id': 1}]):
        with patch('rss2socials.cli.load_seen_links', return_value={'http://example.com/post'}):
            with patch('rss2socials.cli.parse_entry_link_and_date',
                       return_value=('http://example.com/post', datetime.now(timezone.utc))):
                cli.cli_main(fake_ctx)
    assert any('Skipping already seen or old link' in str(call) for call in mock_logger.info.call_args_list)


def test_cli_main_raises_value_error_on_missing_feed_url():
    from rss2socials import cli
    ctx = SimpleNamespace(
        feed_url=None,
        seen_file=':memory:',
        post_age_limit_days=7,
        platforms=['bluesky'],
        log_level='INFO',
    )
    with pytest.raises(ValueError, match="FEED_URL must be provided"):
        cli.cli_main(ctx)
