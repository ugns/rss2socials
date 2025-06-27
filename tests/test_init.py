import sys
import importlib


# --- Version detection logic ---
def test_version_found(monkeypatch):
    import importlib.metadata
    monkeypatch.setattr(importlib.metadata, 'version', lambda name: '1.2.3')
    monkeypatch.setattr(importlib.metadata, 'PackageNotFoundError', Exception)
    import rss2socials
    importlib.reload(rss2socials)
    assert rss2socials.__version__ == '1.2.3'


def test_version_not_found(monkeypatch):
    import importlib.metadata

    class DummyException(Exception):
        pass

    def raise_exc(name):
        raise DummyException('not found')
    monkeypatch.setattr(importlib.metadata, 'version', raise_exc)
    monkeypatch.setattr(importlib.metadata, 'PackageNotFoundError', DummyException)
    import rss2socials
    importlib.reload(rss2socials)
    assert rss2socials.__version__ == '0.0.0-dev'


def test_version_importlib_metadata_fallback(monkeypatch):
    sys.modules.pop('importlib.metadata', None)
    orig_import = __import__

    def fake_import(name, *args, **kwargs):
        if name == 'importlib.metadata':
            raise ImportError('simulate missing importlib.metadata')
        return orig_import(name, *args, **kwargs)
    monkeypatch.setattr('builtins.__import__', fake_import)
    import importlib_metadata
    monkeypatch.setattr(importlib_metadata, 'version', lambda name: '9.9.9')
    monkeypatch.setattr(importlib_metadata, 'PackageNotFoundError', Exception)
    import rss2socials
    importlib.reload(rss2socials)
    assert rss2socials.__version__ == '9.9.9'
