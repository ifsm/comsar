import os
import tempfile
import unittest

from hypothesis import given

from comsar._tracks.utilities import TimbreTrackParams, TrackResult
from utils import timbre_track_results


class TestTrackResult(unittest.TestCase):
    def setUp(self) -> None:
        self.tf_descr, self.tf_name = tempfile.mkstemp(suffix='.json',
                                                       text=True)

    @given(timbre_track_results())
    def test_init(self, ttr) -> None:
        self.assertIsInstance(ttr, TrackResult)

    @given(timbre_track_results())
    def test_to_dict(self, ttr) -> None:
        self.assertIsInstance(ttr.to_dict(), dict)

    @given(timbre_track_results())
    def test_to_json(self, ttr) -> None:
        ttr.to_json(self.tf_name)

    def tearDown(self) -> None:
        os.unlink(self.tf_name)
        os.close(self.tf_descr)
