import unittest
import numpy as np
import pandas as pd

from apollon.tools import time_stamp
from comsar.tracks import TimbreTrack


class TestTimbreTrack(unittest.TestCase):
    def setUp(self):
        self.track = TimbreTrack()

    def test_nfeatures(self):
        self.assertIsInstance(self.track.n_features, int)
