import cv2
import os

from mmir.camera import Camera
from mmir.camera.camera import compute_fundamental_matrix
from mmir.examples.vis_to_flir.config import BASE_PATH, MASK, transform_point_to_initial_flir

from mmir.feature_detection import GFTTFeatureDetector
from mmir.feature_detection.filters import YPositionFilter, XPositionFilter
from mmir.feature_matching import HogFeatureMatcher
from mmir.feature_matching.mi_feature_matcher import MIFeatureMatcher
from mmir.mapping import RansacEstimator, MappingVisualizer
from mmir.pipeline import Pipeline
from skimage.io import imread


def yield_next_images():
    """
    Generator function which returns the next image set to be processed in a form of a tuple
    (vis, flir)
    """
    vis_photos = [os.path.join(BASE_PATH, f) for f in os.listdir(BASE_PATH) if f.endswith("-2.bmp")]
    vis_photos.sort()

    flir_photos = [os.path.join(BASE_PATH, f) for f in os.listdir(BASE_PATH) if f.endswith("-7.bmp")]
    flir_photos.sort()

    for (vis_photo, flir_photo) in zip(vis_photos, flir_photos):
        yield imread(vis_photo), imread(flir_photo)


def preprocess_image_set(vis, flir):
    """
    Preprocessor function for the image set.
    Scales the FLIR photo to the size of the VIS photo, and equalizes the histogram of the VIS
    image.
    """
    flir = cv2.resize(src=flir, dsize=(vis.shape[1], vis.shape[0]))
    return vis, flir


def main():
    flir_camera = Camera.from_files(
        os.path.join(BASE_PATH, 'left_int_F410.txt'),
        os.path.join(BASE_PATH, 'left_ext_F410.txt'),
    )

    vis_camera = Camera.from_files(
        os.path.join(BASE_PATH, 'right_int.txt'),
        os.path.join(BASE_PATH, 'right_ext.txt'),
    )

    fundamental_matrix = compute_fundamental_matrix(
        left_camera=flir_camera,
        right_camera=vis_camera,
    )

    pipline = Pipeline([
        GFTTFeatureDetector(
            subregions=16,
            left_mask=MASK,
            points_per_region=4,
            skip_right=True,
        ),
        GFTTFeatureDetector.visualize,
        MIFeatureMatcher(
            window_size=40,
            filters=[
                YPositionFilter(
                    lower_bound=20,
                    upper_bound=100,
                ),
                XPositionFilter(
                    lower_bound=-32,
                    upper_bound=32,
                ),
            ],
            best_match_threshold=.3,
            matched_point_point_transformer=transform_point_to_initial_flir,
            fundamental_matrix=fundamental_matrix
        ),
        HogFeatureMatcher.visualize,
        RansacEstimator(visualize=True, residual_threshold=4),
        MappingVisualizer(fuse=True),
    ])

    for (right, flir) in yield_next_images():
        (right, flir) = preprocess_image_set(right, flir)
        pipline.run(flir, right)


if __name__ == '__main__':
    main()
