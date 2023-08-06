import numpy as np

from mmir.types import Point, Line, Matrix


def get_epipolar_line(fundamental_matrix: Matrix, point: Point) -> Line:
    """
    Computes the epipolar line, for a given fundamental matrix and point.
    """
    p = np.array([
        point[0],
        point[1],
        1.0
    ], dtype=float)

    return fundamental_matrix @ p
