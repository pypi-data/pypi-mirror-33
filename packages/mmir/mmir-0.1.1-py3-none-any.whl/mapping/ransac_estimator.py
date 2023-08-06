import logging

import cv2
import numpy as np
from skimage.measure import ransac
from skimage.transform import ProjectiveTransform
from skimage.transform._geometric import GeometricTransform

from mmir.feature_matching import Correlations
from mmir.mapping import MappingEstimator, EstimatedMappingModel

LOGGER = logging.getLogger(__name__)


class RansacEstimator(MappingEstimator):
    """
    Uses RANSAC to estimate a given type of model.
    """
    def __init__(
        self,
        model: GeometricTransform = ProjectiveTransform,
        min_samples: int = 4,
        residual_threshold: int = 4,
        visualize: bool=True
    ) -> None:
        self._model = model
        self._min_samples = min_samples
        self._residual_threshold = residual_threshold
        self._visualize = visualize

    def __call__(self, feature_matcher_output: Correlations) -> EstimatedMappingModel:
        left = [l for (l, _, *_) in feature_matcher_output.matches]
        right = [r for (_, r, *_) in feature_matcher_output.matches]

        try:
            model, inliners = ransac(
                (np.array(left), np.array(right)),
                self._model,
                min_samples=self._min_samples,
                residual_threshold=self._residual_threshold,
                max_trials=2000
            )
        except np.linalg.linalg.LinAlgError:
            LOGGER.warning("No convergence...")
            return EstimatedMappingModel(feature_matcher_output.left, feature_matcher_output.right, None)

        filtered_matches = []
        for i, inliner in enumerate(inliners):
            if inliner:
                filtered_matches.append(feature_matcher_output.matches[i])

        if self._visualize:
            left_image = cv2.cvtColor(np.copy(feature_matcher_output.left), cv2.COLOR_GRAY2BGR)
            right_image = cv2.cvtColor(np.copy(feature_matcher_output.right), cv2.COLOR_GRAY2BGR)

            left_image = cv2.resize(src=left_image, dsize=(right_image.shape[1], right_image.shape[0]))

            img = np.concatenate((left_image, right_image), axis=1)

            for i, inliner in enumerate(inliners):
                if not inliner:
                    continue
                pt1 = (int(left[i][0]), int(left[i][1]))
                pt2 = (int(right[i][0] + left_image.shape[1]), int(right[i][1]))

                cv2.line(img=img, pt1=pt1, pt2=pt2, color=(0, 255 if inliner else 0, 0 if inliner else 255))

            cv2.imshow("matches_r", img)

        return EstimatedMappingModel(feature_matcher_output.left, feature_matcher_output.right, model.inverse)
