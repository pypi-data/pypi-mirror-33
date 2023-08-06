import os

import cv2
from mmir.camera import Camera
from mmir.camera.camera import compute_fundamental_matrix
from mmir.feature_detection import GFTTFeatureDetector
from mmir.feature_detection.filters import YPositionFilter, XPositionFilter
from mmir.feature_matching import HogFeatureMatcher
from mmir.mapping import EpipolarTransfer, PolynomialTransformEstimator, MappingVisualizer
from mmir.pipeline import Pipeline
from skimage.io import imread


RSC_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../rsc')


def yield_all_photos():
    left_photos = [os.path.join(RSC_PATH, f) for f in os.listdir(RSC_PATH) if f.endswith("-1.bmp")]
    left_photos.sort()

    right_photos = [os.path.join(RSC_PATH, f) for f in os.listdir(RSC_PATH) if f.endswith("-2.bmp")]
    right_photos.sort()

    flir_photos = [os.path.join(RSC_PATH, f) for f in os.listdir(RSC_PATH) if f.endswith("-7.bmp")]
    flir_photos.sort()

    for (left_photo, right_photo, flir_photo) in zip(left_photos, right_photos, flir_photos):
        yield imread(left_photo), imread(right_photo), imread(flir_photo)


if __name__ == '__main__':
    left_camera = Camera.from_files(
        os.path.join(RSC_PATH, 'left_int.txt'),
        os.path.join(RSC_PATH, 'left_ext.txt'),
    )
    right_camera = Camera.from_files(
        os.path.join(RSC_PATH, 'right_int.txt'),
        os.path.join(RSC_PATH, 'right_ext.txt'),
    )
    flir_camera = Camera.from_files(
        os.path.join(RSC_PATH, 'left_int_F410.txt'),
        os.path.join(RSC_PATH, 'left_ext_F410.txt'),
    )
    left_to_flir = compute_fundamental_matrix(
        left_camera=left_camera,
        right_camera=flir_camera,
    )
    right_to_flir = compute_fundamental_matrix(
        left_camera=right_camera,
        right_camera=flir_camera
    )

    epipolar_transfer = EpipolarTransfer(left_to_flir, right_to_flir)
    pipeline = Pipeline(steps=[
        GFTTFeatureDetector(subregions=16, points_per_region=4, skip_right=True),
        GFTTFeatureDetector.visualize,
        HogFeatureMatcher(
            filters=[
                YPositionFilter(lower_bound=-1, upper_bound=1),
                XPositionFilter(lower_bound=-50, upper_bound=0)
            ],
            best_match_threshold=.2,
        ),
        HogFeatureMatcher.visualize,
        epipolar_transfer,
        PolynomialTransformEstimator(),
        MappingVisualizer(fuse=True)
    ])

    for (left, right, flir) in yield_all_photos():
        epipolar_transfer.destination_image = flir
        pipeline.run(left, right)
        cv2.waitKey(0)
