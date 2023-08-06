import abc
from typing import List, Optional

from dataclasses import dataclass

from mmir.types import Image, Point


@dataclass
class InterestPoints:
    left: Image
    right: Image
    keypoints_left: List[Point]
    keypoints_right: List[Point]


class FeatureDetector(abc.ABC):
    """
    Common interface to be used for the first step of the registration pipeline.

    It defines the input and the output of this pipeline's step.

    It also defines a method for basic visualization of this step.
    """
    def __init__(self, left_mask: Optional[Image]=None, right_mask: Optional[Image]=None):
        """
        :param mask:
            Optional parameter which can be use to mask regions of the image within which
            features should not be computed.
        """
        self._left_mask = left_mask
        self._right_mask = right_mask

    @abc.abstractmethod
    def __call__(self, left_image: Image, right_image: Image) -> InterestPoints:
        pass
