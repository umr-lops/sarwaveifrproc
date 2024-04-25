"""Top-level package for sarwaveifrproc."""

__author__ = """Antoine Grouazel"""
__email__ = 'antoine.grouazel@ifremer.fr'

try:
    from importlib import metadata
except ImportError: # for Python<3.8
    import importlib_metadata as metadata
__version__ = metadata.version('sarwaveifrproc')
