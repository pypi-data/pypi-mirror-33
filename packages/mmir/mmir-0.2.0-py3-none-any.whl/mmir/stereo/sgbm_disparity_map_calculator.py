import cv2
import numpy as np

from mmir.types import Image
from .disparity_map_calculator import DisparityMapCalculator, DisparityMap


class SGBMDisparityMapCalculator(DisparityMapCalculator):
    def __call__(self, left: Image, right: Image, **kwargs) -> DisparityMap:
        min_disp = kwargs.get('min_disp', 0)
        num_disp = kwargs.get('num_disp', 64 - min_disp)
        block_size = kwargs.get('block_size', 5)
        p1 = kwargs.get('p1', 16 * 3 ** 2)
        p2 = kwargs.get('p2', 64 * 3 ** 2)

        left_matcher = cv2.StereoSGBM_create(
            minDisparity=min_disp,
            numDisparities=num_disp,
            blockSize=block_size,
            P1=p1,
            P2=p2,
            mode=cv2.STEREO_SGBM_MODE_SGBM_3WAY,
        )

        right_matcher = cv2.ximgproc.createRightMatcher(left_matcher)
        wls_filter = cv2.ximgproc.createDisparityWLSFilter(left_matcher)

        left_disp = left_matcher.compute(left, right)
        right_disp = right_matcher.compute(right, left)

        disparity_mpap = wls_filter.filter(left_disp, left, None, right_disp).astype(np.float32) / 16.0
        return DisparityMap(left, right, disparity_mpap)

    @staticmethod
    def visualize(output: DisparityMap):
        cv2.imshow("disparity_map", output.disparity_map / 64.0)
        return output
