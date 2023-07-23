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
