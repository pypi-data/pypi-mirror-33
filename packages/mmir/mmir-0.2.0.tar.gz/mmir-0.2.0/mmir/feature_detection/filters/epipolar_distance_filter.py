from typing import List, Generator

from mmir.math.epipolar import get_epipolar_line
from mmir.math.math import point_to_line_distance
from mmir.types import Point, Matrix
from .descriptor_filter import DescriptorsFilter


class EpipolarDistanceFilter(DescriptorsFilter):
    """
    Filters out all the candidate points which are further than a given distance
    away from the epipolar line of the point that is being matched.
    """
    def __init__(self, fundamental_matrix: Matrix, max_distance=5, *args, **kwargs):
        """
        :param fundamental_matrix:
            The fundamental matrix to be used when computing the epipolar line of the point
            that is being matched.
        :param min_distance:
            The maximum admissible distance from the epipolar line a candidate point
            should have to not be filtered out.
        """
        super().__init__(*args, **kwargs)
        self._fundamental_matrix = fundamental_matrix
        self._max_distance = max_distance

    def __call__(self, keypoint: Point, candidate_points: List[Point]) -> Generator[Point, None, None]:
        epipolar_line = get_epipolar_line(
            self._fundamental_matrix,
            self._matched_point_transfomer(keypoint)
        )

        return (
            candidate_point
            for candidate_point
            in candidate_points
            if point_to_line_distance(
                self._candidate_points_transformer(candidate_point),
                epipolar_line
            ) < self._max_distance
        )
