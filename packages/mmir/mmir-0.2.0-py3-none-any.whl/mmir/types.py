from typing import Tuple, List, Union, Optional

import numpy as np

Point = Union[
    Tuple[int, int],
    Tuple[float, float],
    List[int],
    List[float],
    np.array,
]

Line = Union[
    Tuple[int, int, int],
    Tuple[float, float, float],
    List[int],
    List[float],
    np.array,
]

Rectangle = Union[
    Tuple[int, int, int, int],
    Tuple[float, float, float, float],
    List[int],
    List[float],
    np.array,
]

Image = Matrix = Vector = np.array

Match = Tuple[Point, Point, Optional[float]]
