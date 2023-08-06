import cv2

import numpy as np
from dataclasses import dataclass
from multipledispatch import dispatch

from skimage import transform as tf

from mmir.stereo.disparity_transfer import OneToOneMapping
from .mapping_estimator import EstimatedMappingModel
from mmir import Image


@dataclass
class ImageTransformerOutput:
    left: Image
    right: Image
    warped_image: Image


class MappingVisualizer:
    def __init__(self, fuse: bool=False, output_file_path: str=None) -> None:
        self._fuse = fuse
        self._output_file_path = output_file_path

    def _render(self, image: Image):
        if not self._output_file_path:
            cv2.imshow('overlapped' if self._fuse else 'transformed', image)
            cv2.waitKey(0)
            return

        cv2.imwrite(self._output_file_path, image)

    @dispatch(EstimatedMappingModel)
    def __call__(self, mapping_estimator_output: EstimatedMappingModel) -> EstimatedMappingModel:
        warped_image = tf.warp(
            mapping_estimator_output.left,
            mapping_estimator_output.model,
            output_shape=mapping_estimator_output.right.shape

        )

        if self._fuse:
            overlapped = (mapping_estimator_output.right / 255 + warped_image * 3) / 4
            self._render(overlapped)
        else:
            self._render(warped_image)

        return mapping_estimator_output

    @dispatch(OneToOneMapping)
    def __call__(self, disparity_map_calculator_output: OneToOneMapping) -> OneToOneMapping:
        result = np.zeros(disparity_map_calculator_output.left.shape, np.uint8)

        for point in disparity_map_calculator_output.mapping:
            result[(int(point[1][1]), int(point[1][0]))] = \
                disparity_map_calculator_output.right[(int(point[0][1]), int(point[0][0]))]

        if self._fuse:
            overlapped = np.array((result + disparity_map_calculator_output.left / 2) / 1.5, dtype=np.uint8)
            self._render(overlapped)
        else:
            self._render(result)

        return disparity_map_calculator_output

