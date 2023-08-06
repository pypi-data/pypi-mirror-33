from typing import List
import time
from dataclasses import dataclass

from mmir import Image, Match
from mmir.math import get_epipolar_line, line_intersection, point_in_bounds
from .disparity_map_calculator import DisparityMap


@dataclass
class OneToOneMapping:
    left: Image
    right: Image
    mapping: List[Match]


class MappingCalculator:
    def __init__(self, left_to_destination, right_to_destination):
        self._left_to_destination = left_to_destination
        self._right_to_destination = right_to_destination

    def __call__(self, feature_matcher_output: DisparityMap) -> OneToOneMapping:
        transfered_disparity_map = []

        for y in range(0, feature_matcher_output.left.shape[0]):
            for x in range(0, feature_matcher_output.left.shape[1]):
                left_point = (x, y)
                right_point = (x - feature_matcher_output.disparity_map[y, x], y)

                epi_line_from_left = get_epipolar_line(self._left_to_destination, left_point)
                epi_line_from_right = get_epipolar_line(self._right_to_destination, right_point)

                point_in_flir = line_intersection(epi_line_from_left, epi_line_from_right)
                if not point_in_bounds(point_in_flir, feature_matcher_output.right.shape):
                    continue
                transfered_disparity_map.append([point_in_flir, (x, y)])

        return OneToOneMapping(
            feature_matcher_output.left,
            feature_matcher_output.right,
            transfered_disparity_map
        )
