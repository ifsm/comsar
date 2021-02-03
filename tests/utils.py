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
from comsar._tracks import timbre
from comsar._tracks.utilities import TrackMeta, TimbreTrackParams, TrackResult


def ascii_strings() -> SearchStrategy:
    """Strings made of ASCII letters and digits."""
    return  text(sampled_from(string.ascii_letters+string.digits),
                 min_size=2, max_size=10)


def lists_of_strings() -> SearchStrategy:
    """Lists of unique ascii_strings."""
    return lists(ascii_strings(), min_size=2, max_size=10, unique=True)


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
    meta = TrackMeta(comsar.__version__, time_stamp(), 'testfile.wav',
                     draw(ascii_strings()))
    params = TimbreTrackParams(timbre.STFT_DEFAULT,
                               timbre.CORR_DIM_DEFAULT)
    data = draw(numerical_dataframes())
    return TrackResult(meta, params, data)
