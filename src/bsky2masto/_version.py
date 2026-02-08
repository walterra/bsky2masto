from importlib.metadata import PackageNotFoundError, version

try:
    VERSION = version("bsky2masto")
except PackageNotFoundError:
    VERSION = "0.1.0"
