"""bsky2masto package."""

from ._version import VERSION as __version__
from .cli import main

__all__ = ["main", "__version__"]
