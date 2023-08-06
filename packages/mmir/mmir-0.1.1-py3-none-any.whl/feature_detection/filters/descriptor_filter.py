import abc
from typing import Callable, List, Generator

from mmir import Point
from mmir.math.math import identity


class DescriptorsFilter(abc.ABC):
    """
    Defines the interface a descriptor filter should implement.

    A descriptor filter is used to reduce the search space of the search
    for a match of a certain point.

    For example, one good example of a descriptor filter is one that for a given keypoint,
    it filters out all the candidates which are further away than a certain distance from
    the corresponding epipolar line of this point.
    """

    def __init__(
        self,
        matched_point_transformer: Callable[[Point], Point] = identity,
        candidate_points_transformer: Callable[[Point], Point] = identity
    ) -> None:
        """
        Constructs a DescriptorFilter.

        If one wants to transform the coordinates of the keypoint for which the descriptors are
        filtered, or transform the coordinates of the candidates themselves, before applying
        the filters, one can provide callables for these tasks through the following parameter:

        For example, if one of the image is scaled, and your filter works with epipolar lines, you
        might want to transform the points to their original coordinates before doing any
        computations.

        :param matched_point_transformer:
            Function to be called on the point for which candidates are filtered out,
            before applying the filter.
        :param candidate_points_transformer:
            Function to be called on the coordinates of every candidate point, before the
            filter is applied.
        """
        self._matched_point_transfomer = matched_point_transformer
        self._candidate_points_transformer = candidate_points_transformer

    @abc.abstractmethod
    def __call__(self, keypoint: Point, candidate_points: List[Point]) -> Generator[Point, None, None]:
        pass
