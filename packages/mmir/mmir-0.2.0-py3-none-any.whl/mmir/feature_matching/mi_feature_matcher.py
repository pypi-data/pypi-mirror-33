import multiprocessing
from typing import Optional, List, Tuple

import cv2
import numpy as np

from joblib import Parallel, delayed
from mmir.types import Point, Image, Match
from mmir.feature_detection import InterestPoints
from mmir.feature_detection.filters import DescriptorsFilter
from mmir.feature_matching import FeatureMatcher, Correlations
from mmir.math import window_in_bounds, roi, get_epipolar_line, identity


def bresenham(x0, y0, x1, y1, transformer=identity):
    """Yield integer coordinates on the line from (x0, y0) to (x1, y1).

    Input coordinates should be integers.

    The result will contain both the start and the end point.
    """
    dx = x1 - x0
    dy = y1 - y0

    xsign = 1 if dx > 0 else -1
    ysign = 1 if dy > 0 else -1

    dx = abs(dx)
    dy = abs(dy)

    if dx > dy:
        xx, xy, yx, yy = xsign, 0, 0, ysign
    else:
        dx, dy = dy, dx
        xx, xy, yx, yy = 0, ysign, xsign, 0

    D = 2 * dy - dx
    y = 0

    for x in range(dx + 1):
        yield transformer((x0 + x * xx + y * yx, y0 + x * xy + y * yy))
        if D >= 0:
            y += 1
            D -= 2 * dx
        D += 2 * dy


class MIFeatureMatcher(FeatureMatcher):
    """
    Uses HOG (Histogram of Oriented Gradients) to find matches between
    two sets of keypoints of two images.
    """

    def __init__(
            self,
            window_size: int = 40,
            filters: Optional[List[DescriptorsFilter]] = None,
            fundamental_matrix=None,
            matched_point_point_transformer=identity,
            best_match_threshold=None,
            candidate_point_transformer=None,
    ) -> None:
        super().__init__(filters=filters)

        self._window_size = window_size
        self._filters = filters if filters else []
        self._fundamental_matrix = fundamental_matrix
        self._matched_point_transformer = matched_point_point_transformer
        self._best_match_threshold = best_match_threshold
        self._candidate_point_transformer = candidate_point_transformer

    def mi(self, left, right) -> float:
        hist_2d, _, _ = np.histogram2d(
            left.ravel(),
            right.ravel(),
            bins=48
        )
        pxy = hist_2d / float(np.sum(hist_2d))
        px = np.sum(pxy, axis=1)  # marginal for x over y
        py = np.sum(pxy, axis=0)  # marginal for y over x
        px_py = px[:, None] * py[None, :]  # Broadcast to multiply marginals
        nzs = pxy > 0  # Only non-zero pxy values contribute to the sum
        return float(1 - np.sum(pxy[nzs] * np.log(pxy[nzs] / px_py[nzs])))

    def _get_candidate_points(self, matched_point, right: Image):
        epipolar_line = get_epipolar_line(
            self._fundamental_matrix,
            self._matched_point_transformer(matched_point)
        )

        a_r = epipolar_line[0]
        b_r = epipolar_line[1]
        c_r = epipolar_line[2]

        p1x = int(0.0)
        p1y = int(-c_r / b_r)

        p2x = int(right.shape[1])
        p2y = int((-c_r - p2x * a_r) / b_r)

        p3x = int(-c_r / a_r)
        p3y = int(0)

        p4x = int((-b_r * right.shape[0] - c_r) / a_r)
        p4y = int(right.shape[0])

        p1x = max(p1x, p3x)
        p1y = max(p1y, p3y)

        p2x = min(p2x, p4x)
        p2y = min(p2y, p4y)

        return bresenham(p1x, p1y, p2x, p2y)

    def find_match(
            self,
            matched_point: Point,
            left: Image,
            right: Image
    ) -> Optional[Tuple[Point, float]]:
        if not window_in_bounds(center=matched_point, window_size=self._window_size, shape=left.shape):
            return None

        keypoint_subregion = roi(
            center=matched_point,
            width=self._window_size,
            height=self._window_size,
            image=left
        )

        candidate_points = self._get_candidate_points(matched_point, right)

        candidate_points = (
            descriptor for descriptor in candidate_points if window_in_bounds(
                center=descriptor,
                window_size=self._window_size,
                shape=left.shape
            )
        )

        for filter in self._filters:
            candidate_points = filter(matched_point, candidate_points)

        best_match = None
        for candidate_point in candidate_points:
            candidate_subregion = roi(
                center=candidate_point,
                width=self._window_size,
                height=self._window_size,
                image=right,
            )
            distance = self.mi(keypoint_subregion, candidate_subregion)
            if best_match is None or distance < best_match[1]:
                best_match = (candidate_point, distance)

        if not best_match:
            return None

        if self._best_match_threshold is None:
            return best_match

        if best_match[1] > self._best_match_threshold:
            return None

        return best_match

    def find_match_for(self, matched_point: Point, detector_output: InterestPoints) -> Optional[Match]:
        match = self.find_match(
            matched_point,
            detector_output.left,
            detector_output.right
        )

        if not match:
            return None

        return matched_point, match[0], match[1]

    @staticmethod
    def visualize(output: Correlations) -> Image:
        left = cv2.cvtColor(np.copy(output.left), cv2.COLOR_GRAY2BGR)
        right = cv2.cvtColor(np.copy(output.right), cv2.COLOR_GRAY2BGR)

        right = cv2.resize(src=right, dsize=(left.shape[1], left.shape[0]))
        img = np.concatenate((left, right), axis=1)
        for match in output.matches:
            pt1 = (int(match[0][0]), int(match[0][1]))
            pt2 = (int(match[1][0] + output.left.shape[1]), int(match[1][1]))

            cv2.line(img=img, pt1=pt1, pt2=pt2, color=(0, 255, 0))

        cv2.imshow("img", img)
        return output

    def __call__(self, detector_output: InterestPoints) -> Correlations:
        matches = Parallel(n_jobs=8)(
            delayed(self.find_match_for)(keypoint, detector_output) for keypoint in detector_output.keypoints_left
        )

        matches = filter(lambda x: x is not None, matches)
        matches = sorted(matches, key=lambda x: x[2], reverse=True)
        return Correlations(detector_output.left, detector_output.right, matches)
