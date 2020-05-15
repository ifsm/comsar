import pkg_resources as _pkg

from .tracks.timbre import TimbreTrack
from .tracks.utilities import TrackResult

__version__ = _pkg.get_distribution('comsar').version
