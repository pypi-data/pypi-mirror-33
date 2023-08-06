import numpy as np

from skimage import transform as tf

from mmir.feature_matching import Correlations
from mmir.mapping import MappingEstimator, EstimatedMappingModel


class PolynomialTransformEstimator(MappingEstimator):
    """
    Estimates a polynomial transform from the matches found between a couple of images.
    """

    def __call__(self, feature_matcher_output: Correlations) -> EstimatedMappingModel:
        left = [l for (l, _, _) in feature_matcher_output.matches]
        right = [r for (_, r, _) in feature_matcher_output.matches]

        transformation = tf.PolynomialTransform()
        transformation.estimate(np.array(right), np.array(left), order=2)

        return EstimatedMappingModel(feature_matcher_output.left, feature_matcher_output.right, transformation)
