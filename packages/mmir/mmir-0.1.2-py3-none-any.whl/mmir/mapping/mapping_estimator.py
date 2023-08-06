import abc
from typing import Any

from dataclasses import dataclass

from mmir import Image
from mmir.feature_matching import Correlations


@dataclass
class EstimatedMappingModel:
    left: Image
    right: Image
    model: Any


class MappingEstimator(abc.ABC):
    @abc.abstractmethod
    def __call__(self, correlation: Correlations) -> EstimatedMappingModel:
        pass
