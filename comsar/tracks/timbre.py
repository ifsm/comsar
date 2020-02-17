from collections import ChainMap
from dataclasses import dataclass
import pathlib
from timeit import default_timer as timer
from typing import Tuple, Union

import numpy as np
import pandas as pd
import soundfile as sf

from apollon.signal.container import SpectrumParams
from apollon.signal.spectral import Spectrum

from apollon.signal import features, tools
from apollon.audio import fti16
from apollon.tools import scale, standardize


@dataclass
class TTParams:
    segment: dict = {'n_perseg': 2**15, 'n_overlap': 2**14}
    spectrum: SpectrumParams = SpectrumParams(window='hamming',
                                              lcf=50, ucf=10000, ldb=30)
    cdim: dict = {'delay': 14, 'm_dim': 80}
    crr: dict = {'wlen': 300, 'n_delay': 2500})


class TimbreTrack:
    """Compute timbre track of an audio file.
    """
    def __init__(self, path, params: TTParams) -> None:
        """
        Args:
            path:    Path to audio file.
            params:  Feature computation parameters.
        """
        self.path = pathlib.Path(path)
        self.params = params

        self.segments = Segments(self.path, **self.params['segment'])
        self.estimators = ('spectral_centroid', 'spectral_spread', 'splc',
                           'roughness', 'sharpness', 'cdim', 'correlogram')

        self.total_time = 0.0
        self.features = None

    def fit(self)
        """Perform extraction.
        """
        _data = np.zeros((self.segments.n_segs, len(self.estimators)))
        for seg in self.segments:
            print(seg.idx, flush=True)
            _data[seg.idx] = self._extract(seg)

        self.features = pd.DataFrame(data=_data, columns=self.estimators)

    def _extract(self, seg: Segment):
        """Worker
        """
        start = timer()
        y = spectral.Spectrum(self.se)
        y.transform(seg.data)
        ff = {'spectral_centroid': {'frqs': y.frqs, 'bins': y.power},
              'spectral_spread': {'frqs': y.frqs, 'bins': y.power},
              'splc': {'frqs': y.frqs, 'amps': y.abs, 'total': True},
              'roughness_helmholtz': {'frqs': y.frqs, 'bins': y.power, 'frq_max': 100},
              'sharpness': {'frqs': y.frqs.squeeze(), 'bins': y.abs.squeeze()},
              'cdim': {'inp': fti16(seg.data).squeeze(), **self.params['cdim']},
              'correlogram': {'inp': seg.data.squeeze(), **self.params['crr'], 'total': True}
             }

        estimates = [getattr(features, func)(**kwargs).item() for func, kwargs in ff.items()]
        stop = timer() - start
        print(f'{seg.idx}/{self.segments.n_segs}', stop, flush=True)
        return estimates
