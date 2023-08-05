from ._version import get_versions
from .mappings import mappings

__version__ = get_versions()['version']
del get_versions

def to_shortname(name):
    try:
        return mappings[name.lower().replace("-", "")]
    except KeyError:
        return name

