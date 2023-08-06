import os
import numpy as np


def transform_point_to_initial_flir(point):
    return point[0] / Sx, point[1] / Sy


IMAGE_SHAPE = (383, 512)

# The scale ratio between the VIS image and the FLIR image.
# Sx = Width_VIS / Width_FLIR
# Sy = Height_VIS / Height_FLIR
Sx = 1.6
Sy = 1.6

# The patch containing the images
BASE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../rsc')


# The mask we're using for feature detection.
# We're using everything except the dark edges of the FLIR camera, and the FLIR logo.
MASK = np.ones(IMAGE_SHAPE, dtype=np.uint8)
MASK[0:80, 0:512] = 0
MASK[0:383, 470:512] = 0
MASK[0:383, 0:55] = 0
MASK[350:383, 0:512] = 0
