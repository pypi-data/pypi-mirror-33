from typing import Any, Tuple

import numpy as np
from dataclasses import dataclass

from mmir import Matrix, Vector


@dataclass
class Camera:
    # The camera's intrinsic matrix.
    A: Any

    # The camera's translation vector.
    T: Any

    # The camera's rotation matrix.
    R: Any

    @staticmethod
    def from_files(intrinsic_parameters_file_path: str, extrinsic_parameters_file_path: str):
        return Camera(
            read_intrinsic_matrix(intrinsic_parameters_file_path),
            *read_extrinsic_parameters(extrinsic_parameters_file_path)
        )


def read_intrinsic_matrix(path: str) -> Matrix:
    """
    Reads the intrinsic parameters of a camera from a file, assuming the file's format is

    fx fy
    u v

    where fx and fy is the focal length in pixels,
    while (u, v) is the principal point of the camera.

    And returns them in matrix form.
    """
    with open(path) as f:
        lines = f.readlines()

        [fx, fy] = lines[0].split()
        [u, v] = lines[1].split()

        intrinsic_matrix = np.array([
            [fx, 0., u],
            [0., fy, v],
            [0., 0., 1.]
        ], dtype=float)

        return intrinsic_matrix


def read_extrinsic_parameters(path: str) -> Tuple[Vector, Matrix]:
    """
    Reads the extrinsic parameters of a camera from a file, assuming the file's format is

    tx ty tz
    r11 r12 r13
    r21 r22 r23
    r31 r32 r33

    where T = [tx ty tz].T is the translation vector of the camera

              [ r11 r12 r13 ]
    while R = [ r21 r22 r23 ] is the rotation matrix of the camera
              [ r31 r32 r33 ]

    and returns the tuple (T, R).
    """
    with open(path) as f:
        lines = f.readlines()

        tc = np.array(lines[0].split(), dtype=float)
        rc = np.array([line.split() for line in lines[1:4]], dtype=float)

        return tc, rc


def compute_fundamental_matrix(left_camera: Camera, right_camera: Camera) -> Matrix:
    """
    Computes the fundamental matrix relating two cameras
    """
    r_lr = right_camera.R.T @ left_camera.R
    [tx, ty, tz] = left_camera.R @ (right_camera.T - left_camera.T)

    s = np.array([
        [0, -tz, ty],
        [tz, 0, -tx],
        [-ty, tx, 0]
    ])

    e = r_lr @ s
    return np.linalg.inv(right_camera.A).T @ e @ np.linalg.inv(left_camera.A)
