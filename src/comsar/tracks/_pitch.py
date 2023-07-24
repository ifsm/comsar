"""comsar/tracks/pitch.py -- TimbreTack implementation

2022, Rolf Bader
"""
from timeit import default_timer as timer
from typing import Any, Optional

import apollon.audio as apa
import apollon.segment as aps
import apollon.signal.tools as ast
import apollon.tools as apt
import numpy as np
import pandas as pd
from apollon.signal import container, features
from scipy import interpolate

import comsar
from comsar.tracks.models import (
    PitchTrackParams,
    PitchType,
    TonalSystemParams,
    TrackMeta,
    ngramParams,
)
from comsar.tracks.utilities import TrackResult

STFT_DEFAULT = container.StftParams(
    fps=44100,
    window="hamming",
    n_fft=None,
    n_perseg=2205,
    n_overlap=0,
    extend=True,
    pad=True,
)

TONALSYSTEM_DEFAULT = TonalSystemParams(
    dcent=1, dts=0.1, minlen=3, mindev=60, noctaves=8, f0=27.5
)

NGRAM_DEFAULT = ngramParams(
    minnotelength=10, ngram=3, ngcentmin=0, ngcentmax=1200, nngram=10
)

SEGMENTATION_DEFAULT = aps.SegmentationParams(n_perseg=2205, n_overlap=1764, pad=False)


class PitchTrack:
    """Compute PitchTrack of an audio file."""

    def __init__(
        self,
        seg_params: Optional[aps.SegmentationParams] = None,
        tonalsystem_params: Optional[TonalSystemParams] = None,
        ngram_params: Optional[ngramParams] = None,
    ) -> None:
        """
        Args:
            seg_params:         Parameters for Segmentation.
            tonalsystem_params: Parameters for tonal system extraction.
            ngram_params:       Parameters for n-gram computation.

        If any of the arguments is `None`, comsar will fall back to their
        respective default parameters.
        """
        self.params = PitchTrackParams(seg_params or SEGMENTATION_DEFAULT)

        self.TSparams = TonalSystemParams(tonalsystem_params or TONALSYSTEM_DEFAULT)
        self.ngparams = ngramParams(ngram_params or NGRAM_DEFAULT)

        self.cutter = aps.Segmentation(**self.params.segmentation.to_dict())

        self.feature_names = ("Pitch", "SPL")
        self.funcs = [acf_pitch, features.spl]
        self.pace = np.zeros(self.n_features)
        self.verbose = False

    @property
    def n_features(self) -> int:
        """Number of features on track"""
        return len(self.feature_names)

    def extract(
        self, input1: None, input2: Optional[Any] = None, input3: Optional[Any] = None
    ) -> pd.DataFrame:
        """Perform extraction."""
        if type(input1) is str:
            snd = apa.AudioFile(input1)
            segs = self.cutter.transform(snd.data.squeeze())
            args = [(segs.data, snd.fps), (segs.data,)]
        else:
            snd = input1
            fps = int(input2)
            segs = self.cutter.transform(snd.squeeze())
            args = [(segs.data, input2), (segs.data,)]

        kwargs = [{}, {}]

        out = np.zeros((segs.n_segs, self.n_features))
        for i, (fun, arg, kwarg) in enumerate(zip(self.funcs, args, kwargs)):
            out[:, i] = self._worker(i, fun, arg, kwarg)

        if type(input1) is str:
            meta = TrackMeta(comsar.__version__, apt.time_stamp(), snd.file_name)
        else:
            meta = TrackMeta(comsar.__version__, apt.time_stamp(), input3)

        out = pd.DataFrame(data=out, columns=self.feature_names)

        if type(input1) is str:
            snd.close()

        return TrackResult(meta, self.params, out)

    def extract_TonalSystem(
        self,
        data: np.ndarray,
        dcent: float,
        dts: float,
        minlen: int,
        mindev: int,
        noctaves: int,
        f0: float,
    ) -> np.ndarray:
        """Pitch cummulation and Tonal System Extraction

        Args:
            data: Freuencies of adjacent segments of a sound file
            dcent: Accummulation precision in cent. For example, use `dcent` =
                   1 for fine grain extraction, or `dcent` = 100 for semitone
                   grain.
            dts: Standard deviation of tonal system pitch entry used for
                 correlation with accumulated tonal system from sound.
            minlen: Minimum length of adjacent cent values to be accepted as
                    an event (a note, etc.)
            mindev: Minimum deviation allowed to qualify as note in cent.
            noctaves: Number of octaves starting from `f0`. Defaults to
                      `noctaves` = 8.
            f0: Start frequency of octaves Hertz. Defaults to subcontra A at
                `f0` = 27.5.

        Returns:
            c: Cummulated frequency spectrum
            co: Cummulated frequency spectrum within one octave, where the
                frequency of maximum amplitude is vector entry zero and length
                of `co` is defined by `dcent`. Example: with `dcent` = 1,
                `len(co)` = 1200.
            maxf: Frequency of maximum amplitude of cummulated spectrum.
            retNames: Names of the ten best matching scales meeting the input
                      frequency data
            retScale: Theoretical scale values of the ten best matching scales.
            retValue: Contribution of each scale step to the overall
                      correlation for each of the ten best-matching scales.
            retCorr: Overall correlation for the whole scale for each of the
                     ten best-matching scales.
            nnotes: Number of notes in sound.
            notes: Notes of sound as array of `PitchType`, with note type
                   ('note', 'pause', etc.), note start, note stop, note args,
                   where arg1 is note in cent above `f0`.
            cn: Accumulated tonal system spectrum within one octave with
                precision `dcent` from pitch events only, compared to c0
                (see above), which is accululated spectrum over all pitches in
                `data`.

        dcent = self.TSparams.dcent
        print(dcent)
        dts = self.TSparams.dts
        minlen = self.TSparams.minlen
        mindev = self.TSparams.mindev
        noctaves = self.TSparams.noctaves
        f0 = self.TSparams.f0
        """
        scales = pd.read_csv("scales.csv", index_col=0).fillna(0.0)

        root = np.power(2, 1 / (1200 / dcent))
        root1200 = 1 / np.log(root)
        n = int(1200 / dcent * noctaves)
        no = int(float(1200) / float(dcent))

        cent = np.zeros(data.size)
        debug = np.zeros(data.size)
        c = np.zeros(n)
        co = np.zeros(no)

        # Frequency to cent
        for i in range(0, cent.size):
            if data[i] >= f0:
                cent[i] = np.round(np.log(data[i] / f0) * root1200)
            else:
                cent[i] = 0

        # Detect Notes
        # Collection of notes
        notes = []
        # Number of notes
        nnotes = 0
        pos = 0

        while pos < cent.size:
            mean = np.mean(cent[pos : pos + minlen])
            exceeds_over = len(np.where(cent[pos : pos + minlen] > mean + mindev)[0])
            exceeds_under = len(np.where(cent[pos : pos + minlen] < mean - mindev)[0])

            # Within a minimum note length, is there any cent deviation over or under mindev? If not, it is a valid note
            if exceeds_over == 0 and exceeds_under == 0:
                cont = 1
                notecont = True

                # Maybe the note is longer than minlen. Then the note is prolonged until condition fails
                while notecont == True and pos + minlen + cont < cent.size:
                    mean = np.mean(cent[pos : pos + minlen + cont])
                    exceeds_over = len(
                        np.where(cent[pos : pos + minlen + cont] > mean + mindev)[0]
                    )
                    exceeds_under = len(
                        np.where(cent[pos : pos + minlen + cont] < mean - mindev)[0]
                    )

                    if exceeds_over == 0 and exceeds_under == 0:
                        cont = cont + 1
                    # Note has at least one cent = 0, meaning noise
                    elif len(np.where(cent[pos : pos + minlen + cont] == 0)[0]) != 0:
                        pos = pos + minlen + cont
                        notecont = False
                    # Maximum length of note arrived at minlen + cont
                    else:
                        # Accumulate cent values in note and take maximum as pitch of note
                        cn = np.zeros(n)
                        for j in range(pos, pos + minlen + cont - 1):
                            if cent[j] <= n and cent[j] > 0:
                                cn[int(cent[j])] += 1
                        maxa = max(cn)
                        notes.append(
                            PitchType(
                                "note",
                                pos,
                                pos + minlen + cont - 1,
                                np.where(cn == maxa)[0][0],
                                0,
                            )
                        )
                        debug[pos] = notes[nnotes].start
                        pos = pos + minlen + cont
                        nnotes = nnotes + 1
                        notecont = False

            pos = pos + 1

        # Detect tonal system
        # Find strongest pitch in cent over all octaves
        for i in range(1, nnotes):
            for j in range(notes[i].start, notes[i].stop):
                if cent[j] <= n and cent[j] > 0:
                    c[int(cent[j])] += 1

        # Accummulate cents into octave
        maxa = max(c)
        maxs = np.where(c == maxa)[0][0]
        maxf = f0 * np.power(root, maxs)

        # Accumulate pitches into ocatve
        cn = np.zeros(no)
        for i in range(0, nnotes):
            cn[int(np.mod(notes[i].arg1 - maxs, no))] += 1

        # Cummulate cent values into one octave with strongest cent, maxs, as
        # fundamental frequency of tonal system
        for i in range(1, n):
            co[int(np.mod(i - maxs, no))] += c[i]

        co = co / np.linalg.norm(co)

        # Sum amplitudes in co at scale positions matching cent values of all
        # theoretical scales in valiable ts
        ts = np.zeros(scales.shape[0])

        ar = np.arange(0, 1200, dcent)
        for i in range(0, scales.shape[0]):
            ts[i] += co[0]
            for j in range(0, 11):
                if np.logical_not(np.isnan(scales.iloc[i][j] / dcent)):
                    # Correlate each pitch of tonal system as a gauss shape
                    # with calculated tonal system from sound
                    ts[i] += np.sum(
                        co
                        * 2.718281
                        ** (-((scales.iloc[i][j] / dcent - 1 - ar) ** 2) / dts**2)
                    )
                    # aa=np.zeros(no)
                    # aa[int(scales.iloc[i][j]/dcent-1)] = 1
                    # ts[i] += np.sum(co*aa)
                    # ts[i] += co[int(scales.iloc[i][j]/dcent-1)]

        # Detecting the nret = 10 best matching scales in variable tss
        nret = 10
        retNames = np.empty([nret], dtype="object")
        retCorr = np.empty([nret], dtype=float)
        retScale = np.zeros([nret, 13], dtype=int)
        retValue = np.zeros([nret, 13], dtype=float)
        tss = ts
        for i in range(0, nret):
            maxts = max(tss)
            retCorr[i] = maxts
            maxts = np.where(tss == maxts)[0][0]
            retNames[i] = scales.index[maxts]
            retScale[i][0] = 0
            retValue[i][0] = co[0]
            for j in range(0, 11):
                if np.logical_not(np.isnan(scales.iloc[maxts][j])):
                    retScale[i][j + 1] = scales.iloc[maxts][j]
                    retValue[i][j + 1] = co[int(scales.iloc[maxts][j] / dcent) - 1]
            tss[maxts] = 0

        return c, co, maxf, retNames, retScale, retValue, retCorr, nnotes, notes, cn

    def extract_ngram(
        self,
        notes: np.ndarray,
        nnotes: int,
        dcent: int,
        minnotelength: int,
        ngram: int,
        ngcentmin: int,
        ngcentmax: int,
        nngram: int,
    ) -> np.ndarray:
        """
        Args:

            minnotelength: Minimum length of a note to qualify as melody to be
                           used in ngram calculation, value in analysis frames.
            ngram: ngram depth:
                   0: no ngram calculation
                   2: 2-gram,
                   3: 3-gram,
                   4: 4-gram,
                   5: 5-gram.
                   ngram calculation is performed over intervals, not absolute pitches.
            ngcentmin: Minimum interval step in cent to qualify interval to be
                       used in ngram calculation.
            ngcentmax: +-maximum interval to be used for ngram calculation,
                       e.g. 1200 allows for +-1200 cent intervals.
            nngram: number of largest ngram histograms to be calculated,
                    e.g. 10.

        Returns:
            ngrams: array of nngram ngrams, most frequently occuring in sound.
                    For example, 3-gram,nngram = 10, ngcentmax = 1200 ->
                    10 ngrams x 2 intervals (3-grams) = 20 values in array,
                    [ngram 1 1st interval, ngram 1, 2nd interval, ngram 2 1st
                    interval, ngram 2, 2nd interval,...], most frequent ngram first
                    ngram value coding: ngcentmax = 12000 -> +-12 intervals.
                    ngram value = 0 -> -12 half tones, ngram value = 12 -> 0 half
                    tones, ngram value = 24 -> +12 half tones.

            notesinngram: Notes used in ngram calculation as subset of notes
                          applying ninnotelength condition.
        """
        dcent = self.TSparams.dcent
        minnotelength = self.ngparams.mintolength
        ngram = self.ngparams.ngram
        ngcentmin = self.ngparams.ngcentmin
        ngcentmax = self.ngparams.ngcentmax
        nngram = self.ngparams.n

        ngrams = []
        if ngram > 1 and ngram <= 5:
            ngramsall = []
            numgram = 0  # number of different ngrams in sound

            # Calculating ngrams
            notesinngram = []
            # i = 0
            noteindex = []
            for i in range(0, nnotes - ngram):
                step = np.zeros(ngram - 1)

                # Does note qualify for ngram in terms of note length
                if (notes[i].stop - notes[i].start) >= minnotelength:
                    k = 0
                    l = 1
                    kold = 0
                    # Construct ngram
                    while k < ngram - 1 and i + l < nnotes - ngram:
                        # Does note qualify for ngram in terms of note length
                        if (notes[i + l].stop - notes[i + l].start) >= minnotelength:
                            step[k] = notes[i + l].arg1 - notes[i + kold].arg1
                            k += 1
                            kold = l
                            l += 1
                        else:
                            l += 1
                    # Is ngram within defined region of ngcentmin and ngcentmax
                    if len(
                        [
                            x
                            for x in step
                            if np.abs(x) >= ngcentmin / dcent
                            and np.abs(x) <= ngcentmax / dcent
                        ]
                    ) == (ngram - 1):
                        ngramsall.append(step)
                        numgram += 1
                        notesinngram.append(notes[i])

            # Calculating ngram histogram and seeking for nngram most frequent
            # ngrams. Equidistant 12-tone tonal system used
            justint = 100
            ngrams = np.zeros((ngram - 1) * nngram)
            histrange = int(ngcentmax / justint)
            sh = np.arange(ngram - 1)
            for i in range(0, ngram - 1):
                sh[i] = 2 * histrange + 1
            hist = np.zeros(shape=sh)
            for i in range(0, numgram):
                wo = (int(ngramsall[i][0] / justint + histrange),)
                for k in range(1, ngram - 1):
                    wo = wo + (int(ngramsall[i][k] / justint + histrange),)
                hist[wo] += 1

            nmax = 0
            while nmax < nngram:
                # number of positions with maximum ngram occurance could be larger than 1
                nn = len(np.where(hist == hist.max())[0])
                # Allow only up to nngram
                if (nmax + nn) > nngram:
                    nn = nngram - nmax
                    # print('hinaus')
                maxvals = np.where(hist == hist.max())
                for i in range(0, nn):
                    for k in range(0, ngram - 1):
                        ngrams[(nmax + i) * (ngram - 1) + k] = maxvals[k][i]
                    wo = (int(ngrams[(nmax + i) * (ngram - 1)]),)
                    for k in range(1, ngram - 1):
                        wo = wo + (int(ngrams[(nmax + i) * (ngram - 1) + k]),)
                    hist[wo] = 0
                nmax += nn

        return ngrams, notesinngram

    def _worker(self, idx, func, args, kwargs) -> np.ndarray:
        print(self.feature_names[idx], end=" ... ")
        pace = timer()
        res = func(*args, **kwargs)
        pace = timer() - pace
        self.pace[idx] = pace
        print(f"{pace:.4} s.")
        return res


def acf_pitch(sig: np.ndarray, fps: int, **kwargs) -> np.ndarray:
    """Pitch estimation with auto-correlation."""
    ptch = np.zeros(sig.shape[1])
    acf_seg = np.array([ast.acf(__s) for __s in np.atleast_2d(sig).T])
    first_zero_d_acf = np.argmax(np.diff(acf_seg < 0), axis=1)
    n_perseg = sig.shape[0]

    for i, (fzda, acs) in enumerate(zip(first_zero_d_acf, acf_seg)):
        if fzda > 0:
            max_acf = np.max(acs[fzda:])
            max_idx = np.argmax(acs == max_acf)

            ptch[i] = fps / max_idx

            # Detect artifacts
            R = np.mod(n_perseg, fps / (ptch[i] * 2))
            p = fps / (ptch[i] * 2)
            if R < p / 2:
                ptch[i] = ptch[i] - p * np.sin(2 * np.pi * R / (2 * p)) / (n_perseg)
            else:
                ptch[i] = ptch[i] - p * np.sin(2 * np.pi * (p - R) / (2 * p)) / (
                    n_perseg
                )

            if ptch[i] > 1720:
                ninterpol = 10
                sec = range(0, sig.data.shape[0])
                secnew = np.arange(0, sig.data.shape[0], 1 / ninterpol)
                org = sig[:, i]
                tck = interpolate.splrep(sec, org, s=0)
                f = interpolate.splev(secnew, tck, der=0)

                amp = np.zeros(ninterpol * 2)
                for j in range(0, ninterpol * 2):
                    delay = int(fps / ptch[i]) * ninterpol - ninterpol + j
                    f1 = np.concatenate((np.zeros(delay), f[0 : f.size - delay]))
                    amp[j] = f / np.linalg.norm(f) @ f1 / np.linalg.norm(f1)

                maxa = np.max(amp)
                maxw = np.argmax(amp == maxa)

                ptch[i] = fps / (max_idx - 1 + maxw / ninterpol)
    return ptch
