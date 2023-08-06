from mmir.feature_matching import Correlations
from mmir.math import get_epipolar_line, line_intersection


class EpipolarTransfer:
    def __init__(self, left_to_destination, right_to_destination, transfer_right_matches: bool = True):
        self._left_to_destination = left_to_destination
        self._right_to_destionation = right_to_destination
        self._transfer_right_matches = transfer_right_matches

        self.destination_image = None

    def __call__(self, feature_matcher_output: Correlations) -> Correlations:
        flir_points = []

        for match in feature_matcher_output.matches:
            left_point = match[0]
            right_point = match[1]

            epi_line_from_left = get_epipolar_line(self._left_to_destination, left_point)
            epi_line_from_right = get_epipolar_line(self._right_to_destionation, right_point)

            point_in_flir = line_intersection(epi_line_from_left, epi_line_from_right)

            flir_points.append(point_in_flir)

        final_matches = []
        for i in range(0, len(flir_points)):
            final_matches.append((
                flir_points[i],
                feature_matcher_output.matches[i][1 if self._transfer_right_matches else 0],
                1
            ))

        feature_matcher_output.matches = final_matches
        feature_matcher_output.left = self.destination_image
        return feature_matcher_output
