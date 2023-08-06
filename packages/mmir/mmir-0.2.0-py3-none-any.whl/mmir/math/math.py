from typing import Any

import numpy as np

from mmir.types import Point, Line, Rectangle, Image


def point_to_line_distance(point: Point, line: Line) -> float:
    """
    Computes the distance between a line and a point
    """

    a_r = line[0]
    b_r = line[1]
    c_r = line[2]

    distance = abs(a_r * point[0] + b_r * point[1] + c_r) / ((a_r ** 2 + b_r ** 2) ** 0.5)
    return distance


def line_intersection(line_a: Line, line_b: Line) -> Point:
    """
    Computes the intersection of two lines.
    """
    a = line_a[0]
    b = line_a[1]
    c = line_a[2]

    j = line_b[0]
    k = line_b[1]
    l = line_b[2]

    y = (a * l - c * j) / (b * j - a * k)
    x = (c * k - b * l) / (b * j - a * k)

    return x, y


def ssd(x: np.array, y: np.array) -> float:
    """
    Computes the euclidean distance between two np.arrays.
    """
    return np.linalg.norm(x - y)


def window_in_bounds(center: Point, window_size: int, shape: Rectangle) -> bool:
    """
    Checks if a window centered in a given point, with a given size,
    can fit in a rectangle with a given shape.

    :param center:
        The center of the window
    :param window_size:
        The window's size
    :param shape:
        The shape of the rectangle against which the check is made.
        The expected shape is in the form (rows, cols) as is
        traditional in numpy.
    """

    [x, y] = center

    return not (
        x < window_size / 2 or
        x > shape[1] - window_size / 2 or
        y < window_size / 2 or
        y > shape[0] - window_size / 2
    )


def point_in_bounds(point: Point, shape: Rectangle) -> bool:
    """
    Checks if a point can fit in a rectangle with a given shape.
    """
    [x, y] = point

    return not (
        x < 0 or
        x >= shape[1] or
        y < 0 or
        y >= shape[0]
    )


def roi(center: Point, width: int, height: int, image: Image) -> Image:
    """
    Crops a ROI from an image.
    :param center:
        The center of the ROI.
    :param width:
        The width of the ROI.
    :param height:
        The height of the ROI.
    :param image:
        The image from which to crop the ROI.
    """
    [x, y] = center
    return image[
       int(y - height // 2):int(y + height // 2),
       int(x - width // 2):int(x + width // 2)
    ]


def identity(x: Any) -> Any:
    """
    Identity function. Returns whatever entity it receives.
    """
    return x
