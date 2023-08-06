import abc

from typing import List, Optional

from dataclasses import dataclass

from mmir.feature_detection import InterestPoints
from mmir.feature_detection.filters import DescriptorsFilter
from mmir.types import Image, Match


@dataclass
class Correlations:
    left: Image
    right: Image
    matches: List[Match]


class FeatureMatcher(abc.ABC):
    """
    Common interface to be used for the matching step of the registration pipeline.

    It defines the input and the output of this pipeline's step.

    It also defines a static method for basic visualization of the matching.
    """
    def __init__(self, filters: Optional[List[DescriptorsFilter]]):
        """
        :param filters:
            When figuring out the matching candidates of one point,
            optional filters will be applied to reduce the search space.

            For example, for a point on the left image, one might only
            consider the features from the right image close to the epipolar line
            corresponding to this point.
        """
        self._filters = filters

    @abc.abstractmethod
    def __call__(self, features: InterestPoints) -> Correlations:
        pass
