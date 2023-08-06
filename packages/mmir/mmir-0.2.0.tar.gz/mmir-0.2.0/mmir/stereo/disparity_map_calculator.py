import abc

from dataclasses import dataclass

from mmir.types import Image


@dataclass
class DisparityMap:
    left: Image
    right: Image
    disparity_map: Image


class DisparityMapCalculator(abc.ABC):
    """
    Abstract class to define the behavior of a disparity map computation step.
    """
    @abc.abstractmethod
    def __call__(self, left: Image, right: Image, **kwargs) -> DisparityMap:
        pass





