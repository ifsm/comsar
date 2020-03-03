from dataclasses import dataclass
import pathlib
from timeit import default_timer as timer

import numpy as np
import pandas as pd

from apollon.audio import AudioFile
from apollon.segment import Segmentation, Segments
from apollon.signal.container import STParams
from apollon.signal.spectral import StftSegments
from apollon.signal import features
from apollon.tools import standardize


segment_default = {'n_perseg': 2**15, 'n_overlap': 2**14, 'extend': True, 'pad': True}
cdim_default = {'delay': 14, 'm_dim': 80, 'n_bins': 1000, 'scaling_size': 10}
crr_default = {'wlen': 2**9, 'n_delay': 2**10, 'total': True}

@dataclass
class TTParams:
    segment: dict
    cdim: dict
    crr: dict


class TimbreTrack:
    """Compute timbre track of an audio file.
    """
    def __init__(self, path, segment_params: dict = segment_default,
                 cdim_params: dict = cdim_default,
                 crr_params: dict = crr_default) -> None:
        """
        Args:
            path:    Path to audio file.
            params:  Feature computation parameters.
        """
        self.params = TTParams(segment_params, cdim_params, crr_params)
        self.path = pathlib.Path(path)
        snd = AudioFile(path)
        cutter = Segmentation(**self.params.segment)
        self.segments = cutter.transform(snd.data.squeeze())
        stp = STParams(snd.fps)
        stft = StftSegments(stp)
        self.spectrogram = stft.transform(self.segments)
        self.feature_names = ('Spectral Centroid', 'Spectral Spread',
                              'Spectral Flux', 'Roughness', 'Sharpness',
                              'SPL', 'Correlation Dimension', 'Correlogram')
        self.funcs = [features.spectral_centroid, features.spectral_spread,
                      features.spectral_flux, features.roughness_helmholtz,
                      features.sharpness, features.spl, features.cdim,
                      features.correlogram]

        assert len(self.feature_names) == len(self.funcs)

        self._features = np.zeros((self.segments.n_segs, self.n_features))
        self.pace = np.zeros(self.n_features)
        self.verbose = False
        snd.close()

    @property
    def n_features(self) -> int:
        return len(self.feature_names)

    @property
    def features(self) pd.DataFrame:
        if self._features is None:
            return None
        return pd.DataFrame(data=self._features,
                            columns=self.feature_names)

    @property
    def z_score(self) -> pd.Dataframe:
        if self._features is None:
            return None
        return standardize(self.features)


    def extract(self) -> None:
        """Perform extraction.
        """
        args = [(self.spectrogram.frqs, self.spectrogram.power),
                (self.spectrogram.frqs, self.spectrogram.power),
                (self.spectrogram.abs,),
                (self.spectrogram.d_frq, self.spectrogram.abs, 15000),
                (self.spectrogram.frqs, self.spectrogram.abs),
                (self.segments._segs,),
                (self.segments._segs,),
                (self.segments._segs,)]

        kwargs = [{}, {}, {}, {}, {}, {}, self.params.cdim,
                 self.params.crr]
        for i, (fun, arg, kwarg) in enumerate(zip(self.funcs, args, kwargs)):
            self._worker(i, fun, arg, kwarg)

    def _worker(self, idx, func, args, kwargs) -> None:
        print(self.feature_names[idx], end=' ... ')
        pace = timer()
        self._features[:, idx] = func(*args, **kwargs)
        pace = timer() - pace
        self.pace[idx] = pace
        print(f'{pace:.4} s.')
