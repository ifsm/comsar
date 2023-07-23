"""
Utilities for testing.
"""
import string

from hypothesis.strategies import (composite, integers, lists, sampled_from,
        text, SearchStrategy)
from hypothesis.extra.numpy import arrays
import pandas as pd
from apollon.tools import time_stamp

import comsar
from comsar.tracks._timbre import STFT_DEFAULT, CORR_DIM_DEFAULT
from comsar.tracks.models import SourceMeta, TrackMeta, TimbreTrackParams
from comsar.tracks.utilities import TrackResult


def ascii_strings() -> SearchStrategy:
    """Strings made of ASCII letters and digits."""
    return  text(sampled_from(string.ascii_letters+string.digits),
                 min_size=2, max_size=10)


def sha1_hexdigests() -> SearchStrategy:
    """Strings that look like hex digest from SHA1."""
    return  text(sampled_from(string.ascii_lowercase+string.digits),
                 min_size=40, max_size=40)


def lists_of_strings() -> SearchStrategy:
    """Lists of unique ascii_strings."""
    return lists(ascii_strings(), min_size=2, max_size=10, unique=True)


def prependdot(b: str) -> str:
    return f".{b}"
    

def file_extensions() -> SearchStrategy:
    """File extensions"""
    return text(sampled_from(string.ascii_letters+string.digits),
                min_size=1, max_size=10).map(prependdot)


@composite
def source_metas(draw) -> SourceMeta:
    """Generate instances of ``SourceMeta``"""
    name = draw(ascii_strings())
    extension = draw(file_extensions())
    hash_ = draw(sha1_hexdigests())
    return SourceMeta(name=name, extension=extension, hash_=hash_)


@composite
def numerical_dataframes(draw) -> pd.DataFrame:
    """Generate pandas DataFrames.

    Each column is of type np.float64. Shape vaies between
    (1, 2) and (1000, 10).
    """
    names = draw(lists_of_strings())
    n_rows = draw(integers(min_value=1, max_value=1000))
    data = draw(arrays('float64', (n_rows, len(names))))
    return pd.DataFrame(data=data, columns=names)


@composite
def timbre_track_results(draw) -> TrackResult:
    """Mock the result of a timbre track extraction pipeline.
    """
    meta = TrackMeta(version=comsar.__version__, extraction_date=time_stamp(),
                     source=draw(source_metas())) 
    params = TimbreTrackParams(STFT_DEFAULT, CORR_DIM_DEFAULT)
    data = draw(numerical_dataframes())
    return TrackResult(meta, params, data)
