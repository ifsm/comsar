import unittest
import numpy as np
import pandas as pd

from apollon.tools import time_stamp
from comsar.tracks.timbre import (TimbreTrack,
    STFT_DEFAULT, CORR_DIM_DEFAULT, CORR_GRAM_DEFAULT)
import comsar
from comsar.tracks.utilities import TrackMeta, TrackParams, TrackResult, TimbreTrackParams


class TestTimbreTrack(unittest.TestCase):
    def setUp(self):
        self.track = TimbreTrack()

    def test_nfeatures(self):
        self.assertIsInstance(self.track.n_features, int)


