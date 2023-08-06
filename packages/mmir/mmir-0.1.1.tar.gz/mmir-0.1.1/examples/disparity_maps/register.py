import os
import cv2

from mmir.camera.camera import Camera, compute_fundamental_matrix
from mmir.mapping import MappingVisualizer
from mmir.pipeline import Pipeline
from mmir.pipeline.interceptor import Interceptor
from mmir.stereo.disparity_transfer import MappingCalculator, OneToOneMapping
from mmir.stereo.sgbm_disparity_map_calculator import SGBMDisparityMapCalculator

RSC_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../rsc')


def yield_all_photos():
    left_photos = [os.path.join(RSC_PATH, f) for f in os.listdir(RSC_PATH) if f.endswith("-1.bmp")]
    left_photos.sort()

    right_photos = [os.path.join(RSC_PATH, f) for f in os.listdir(RSC_PATH) if f.endswith("-2.bmp")]
    right_photos.sort()

    flir_photos = [os.path.join(RSC_PATH, f) for f in os.listdir(RSC_PATH) if f.endswith("-7.bmp")]
    flir_photos.sort()

    for i in range(0, len(left_photos)):
        left = cv2.imread(left_photos[i], cv2.IMREAD_GRAYSCALE)
        right = cv2.imread(right_photos[i], cv2.IMREAD_GRAYSCALE)
        flir = cv2.imread(flir_photos[i], cv2.IMREAD_GRAYSCALE)

        yield left, right, flir


def main():
    flir_camera = Camera.from_files(
        os.path.join(RSC_PATH, 'left_int_F410.txt'),
        os.path.join(RSC_PATH, 'left_ext_F410.txt'),
    )

    left_camera = Camera.from_files(
        os.path.join(RSC_PATH, 'left_int.txt'),
        os.path.join(RSC_PATH, 'left_ext.txt'),
    )

    right_camera = Camera.from_files(
        os.path.join(RSC_PATH, 'right_int.txt'),
        os.path.join(RSC_PATH, 'right_ext.txt'),
    )

    left_to_flir = compute_fundamental_matrix(left_camera, flir_camera)
    right_to_flir = compute_fundamental_matrix(right_camera, flir_camera)

    interceptor = Interceptor()
    pipeline = Pipeline([
        SGBMDisparityMapCalculator(),
        SGBMDisparityMapCalculator.visualize,
        MappingCalculator(left_to_flir, right_to_flir),
        interceptor,
        MappingVisualizer(fuse=True),
    ])

    for (left, right, flir) in yield_all_photos():
        interceptor.intercept = lambda output: OneToOneMapping(output.left, flir, output.mapping)
        pipeline.run(left, right)


if __name__ == '__main__':
    main()
