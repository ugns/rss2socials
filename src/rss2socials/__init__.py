try:
    from importlib.metadata import version, PackageNotFoundError
except ImportError:
    from importlib_metadata import version, PackageNotFoundError  # for Python <3.8

try:
    __version__ = version("rss2socials")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"  # fallback when package isn't installed (e.g., during development)

__all__ = ["__version__"]
