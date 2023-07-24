"""comsar/tracks/untilities.py -- Utilities
"""
import pathlib
import pickle
from typing import Type, TypeVar, Union

import numpy as np
import pandas as pd
from apollon import io
from apollon.tools import standardize

from .models import TimbreTrackParams, TrackMeta, TrackParams

T = TypeVar("T", bound="TrackResult")


class TrackResult:
    """Provide track results."""

    def __init__(
        self, meta: TrackMeta, params: TrackParams, data: pd.DataFrame
    ) -> None:
        self._meta = meta
        self._params = params
        self._data = data

    @property
    def data(self) -> np.ndarray:
        """Return the raw data array."""
        return self._data.to_numpy()

    @property
    def features(self) -> pd.DataFrame:
        """Extracted feautures."""
        return self._data

    @property
    def features_names(self) -> list:
        """Name of each feature."""
        return self._data.columns.to_list()

    @property
    def z_score(self) -> pd.DataFrame:
        """Z-score of extracted features."""
        return standardize(self.features)

    def to_csv(self, path: Union[str, pathlib.Path]) -> None:
        """Serialize features to csv file.

        This does not save parameters, and meta data.

        Args:
            path:  Destination path.
        """
        self._data.to_csv(path)

    def to_dict(self) -> dict:
        """Serialize TrackResults to dictionary."""
        return {
            "meta": self._meta.to_dict(),
            "params": self._params.to_dict(),
            "data": self._data.to_dict(orient="list"),
        }

    def to_json(self, path: Union[str, pathlib.Path]) -> None:
        """Serialize TrackResults to JSON."""
        io.json.dump(self.to_dict(), path)

    def to_mongo(self, db_con) -> None:
        """Write TrackResults to open MongoDB connection:"""
        pass

    def to_pickle(self, path: Union[str, pathlib.Path]) -> None:
        """Serialize Track Results to pickle."""
        path = pathlib.Path(path)
        with path.open("wb") as fobj:
            pickle.dump(self, fobj)

    @classmethod
    def read_json(cls: Type[T], path: Union[str, pathlib.Path]) -> T:
        """Read TrackResults form json."""
        raw = io.json.load(path)
        meta = TrackMeta.from_dict(raw["meta"])
        params = TimbreTrackParams.from_dict(raw["params"])
        data = pd.DataFrame(raw["data"])
        return cls(meta, params, data)

    @classmethod
    def read_pickle(cls: Type[T], path: Union[str, pathlib.Path]) -> T:
        """Read pickled TrackResults."""
        path = pathlib.Path(path)
        with path.open("rb") as fobj:
            return pickle.load(fobj)
