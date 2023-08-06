from typing import Optional, List, Tuple

import cv2
import numpy as np
from joblib import Parallel, delayed
from skimage import feature

from mmir import Point, Image, Match
from mmir.feature_detection import InterestPoints
from mmir.feature_detection.filters import DescriptorsFilter
from mmir.feature_matching import FeatureMatcher, Correlations
from mmir.math import window_in_bounds, roi, ssd


class HogFeatureMatcher(FeatureMatcher):
    """
    Uses HOG (Histogram of Oriented Gradients) to find matches between
    two sets of keypoints of two images.
    """

    def __init__(
            self,
            window_size: int = 40,
            filters: Optional[List[DescriptorsFilter]] = None,
            best_match_threshold: float = .9,
    ) -> None:
        """
        :param window_size:
            The size of the window centered in the keypoint used for computing the HOG
            which is used for feature matching.
        :param measure:
            The measure to be used for comparing the distance between two HOG feature
            vectors.
        :param filters:
            Filters to be used for deciding on the candidate descriptors for a match.
        """
        super().__init__(filters=filters)

        self._window_size = window_size
        self._filters = filters if filters else []
        self._best_match_threshold = best_match_threshold

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

        candidate_points = (
            [x, matched_point[1]] for x in range(0, right.shape[1])
        )

        candidate_points = (
            descriptor for descriptor in candidate_points if window_in_bounds(
                center=descriptor,
                window_size=self._window_size,
                shape=left.shape
            )
        )

        for filter in self._filters:
            candidate_points = filter(matched_point, candidate_points)

        reference_hog = feature.hog(keypoint_subregion, block_norm='L1')
        best_match = None
        for candidate_point in candidate_points:
            candidate_subregion = roi(
                center=candidate_point,
                width=self._window_size,
                height=self._window_size,
                image=right,
            )
            candidate_hog = feature.hog(candidate_subregion, block_norm='L1')
            distance = ssd(reference_hog, candidate_hog)
            if best_match is None or distance < best_match[1]:
                best_match = (candidate_point, distance)

        if self._best_match_threshold is None:
            return best_match

        if not best_match:
            return best_match

        if best_match[1] < self._best_match_threshold:
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

        matches = list(filter(lambda x: x is not None, matches))
        matches = sorted(matches, key=lambda x: x[2], reverse=True)

        return Correlations(detector_output.left, detector_output.right, matches)
