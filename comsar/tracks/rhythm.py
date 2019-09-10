# Licensed under the terms of the BSD-3-Clause license.
# Copyright (C) 2019 Michael Blaß
# michael.blass@uni-hamburg.de

import logging

from apollon.signal import spectral
from apollon import tools
from apollon import onsets
from apollon import segment


def rhythm_track(snd: AudioFile) -> dict:
    """Perform rhythm track analysis of given audio file.

    Args:
        snd:  Sound data.
        fps:  Sample rate.

    Returns:
        Rhythm track parameters and data.
    """
    logging.info('Starting rhythm track for {!s}'.format(snd.file))
    onsets = FluxOnsetDetector(snd.data, snd.fps)
    segs = segment.by_onsets(snd.data, 2**11, onsets.index())
    spctr = Spectrum(segs, snd.fps, window='hamming', n_fft=2**15)

    onsets_features = {
        'peaks': onsets.peaks,
        'index': onsets.index(),
        'times': onsets.times(snd.fps)
    }

    track_data = {
        'meta': {'source': str(snd.file.absolute()),
                 'time_stamp': time_stamp()},
        'params': {'onsets': onsets.params(), 'spectrum': spctr.params()},
        'features': {'onsets': onsets_features,
                     'spectrum':
                      spctr.extract(cf_low=100, cf_high=9000).as_dict()}
    }
    logging.info(f'Done with rhythm track for {snd.file!s}.')
    return track_data
