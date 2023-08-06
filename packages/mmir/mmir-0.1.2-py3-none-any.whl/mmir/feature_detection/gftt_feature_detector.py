from typing import List, Optional

import cv2
import numpy as np

from mmir import Point, Image
from .feature_detector import FeatureDetector, InterestPoints


class GFTTFeatureDetector(FeatureDetector):
    """
    Feature detection using openCV's goodFeaturesToTrack function.
    """
    def __init__(self, subregions: int=1, points_per_region=30, skip_right=False, *args, **kwargs):
        """
        :param subregions:
            If you want to apply GFTT on subregions instead of the whole image,
            use this parameter too specify in how many subregions should the image
            be split in.
        """
        assert subregions > 0
        super().__init__(*args, **kwargs)

        self._points_per_region = points_per_region
        self._subregions = subregions
        self._skip_right = skip_right


    @staticmethod
    def visualize(output: InterestPoints) -> Image:
        left = np.copy(output.left)
        right = np.copy(output.right)

        left = cv2.cvtColor(left, cv2.COLOR_GRAY2BGR)
        right = cv2.cvtColor(right, cv2.COLOR_GRAY2BGR)

        for keypoint in output.keypoints_left:
            cv2.circle(left, (int(keypoint[0]), int(keypoint[1])), 1, (0, 0, 255))

        for keypoint in output.keypoints_right:
            cv2.circle(right, (int(keypoint[0]), int(keypoint[1])), 1, (0, 0, 255))

        cv2.imshow("featureDetector", np.concatenate((left, right), axis=1))
        return output

    def _filter_masked_interest_points(self, interest_points: List[Point], mask: Optional[Image]=None) -> List[Point]:
        """
        Excludes the interest points which are masked out, if a mask is specified.
        """
        if mask is None:
            return interest_points

        return [feature for feature in interest_points if mask[(feature[1], feature[0])]]

    def _interest_points_from_subregion(
        self,
        subregion: Image,
        x_offset: int,
        y_offset: int,
        mask: Optional[Image]=None
    ):
        """
        Applies GFTT on a subregion of the original image, and returns the interest points
        of this subregion.

        The offset parameters are used to map the coordinates of the interest points from
        the coordinate system of the subregion to the coordinate system of the entire image.

        :param subregion:
            The subregion on which GFTT should be applied.
        :param y_offset:
            The y coordinate of the region.
        :param x_offset:
            The x coordinate of the region.
        :return:
        """
        features = cv2.goodFeaturesToTrack(subregion, self._points_per_region, 0.1, 0)
        features = [feature[0] for feature in features] if features is not None else []
        features = [(int(feature[0]) + x_offset, int(feature[1]) + y_offset) for feature in features]
        return self._filter_masked_interest_points(features, mask)

    def _find_interest_points_in_subregions(
        self,
        left: Image,
        right: Image
    ) -> InterestPoints:
        """
        Finds the interest points of every subregion and unifies the results.
        """
        cols = left.shape[1]
        rows = left.shape[0]

        left_corners = []
        right_corners = []

        y_step = rows // self._subregions
        x_step = cols // self._subregions

        for y_offset in range(0, rows, y_step):
            for x_offset in range(0, cols, x_step):
                left_subregion = left[y_offset:y_offset + y_step, x_offset:x_offset + x_step]
                left_corners.extend(
                    self._interest_points_from_subregion(left_subregion, x_offset, y_offset, self._left_mask)
                )

                if not self._skip_right:
                    right_subregion = right[y_offset:y_offset + y_step, x_offset:x_offset + x_step]
                    right_corners.extend(
                        self._interest_points_from_subregion(right_subregion, x_offset, y_offset, self._right_mask)
                    )

        output = InterestPoints(left, right, left_corners, right_corners)

        return output

    def __call__(self, left: Image, right: Image) -> InterestPoints:
        if self._subregions != 1:
            return self._find_interest_points_in_subregions(left, right)

        left_keypoints = cv2.goodFeaturesToTrack(left, 300, 0.0000001, 0, mask=self._left_mask)
        left_keypoints = [kp[0] for kp in left_keypoints]

        right_keypoints = []
        if not self._skip_right:
            right_keypoints = cv2.goodFeaturesToTrack(right, 500, 0.000000001, 0, mask=self._right_mask)
            right_keypoints = [kp[0] for kp in right_keypoints]

        output = InterestPoints(left, right, left_keypoints, right_keypoints)

        return output
