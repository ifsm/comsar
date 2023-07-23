from dataclasses import dataclass
from datetime import datetime
from typing import ClassVar

from apollon.container import Params
from apollon.signal.container import StftParams, CorrDimParams, CorrGramParams
from apollon import types


@dataclass
class SourceMeta(Params):
    """Source file meta data."""
    _schema: ClassVar[types.Schema] = None
    name: str
    extension: str
    hash_: str


@dataclass
class TrackMeta(Params):
    """Track meta data."""
    _schema: ClassVar[types.Schema] = None
    version: str
    extraction_date: datetime
    source: SourceMeta


@dataclass
class TrackParams(Params):
    """Track parameter base class."""
    _schema: ClassVar[types.Schema] = None


@dataclass
class TimbreTrackParams(TrackParams):
    """Parameter set for TimbreTrack"""
    stft: StftParams
    corr_dim: CorrDimParams


@dataclass
class TimbreTrackCorrGramParams(TrackParams):
    """Parameter set for TimbreTrack"""
    stft: StftParams
    corr_dim: CorrDimParams
    corr_gram: CorrGramParams


@dataclass
class TonalSystemParams(Params):
    """Parameter set for Tonal System analysis"""
    #_schema: ClassVar[types.Schema] = io.json.load_schema('TonalSystem')
    dcent: int = 1
    dts: float = 0.1
    minlen: int = 3
    mindev: int = 60
    noctaves: int = 8
    f0: float = 27.5


@dataclass
class ngramParams(Params):
    """Parameter set for n-gram analysis"""
    #_schema: ClassVar[types.Schema] = io.json.load_schema('ngram')
    minnotelength: int = 10
    ngram: int = 3
    ngcentmin: int = 0
    ngcentmax: int = 1200
    nngram: int = 10
