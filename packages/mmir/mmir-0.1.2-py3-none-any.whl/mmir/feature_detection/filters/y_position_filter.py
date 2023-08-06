from typing import Callable, List, Generator, Optional, Union

from mmir import Point
from .descriptor_filter import DescriptorsFilter


class YPositionFilter(DescriptorsFilter):
    """
    Filters out all the descriptors which have y coordinate
    outside the range (lower_bound(matched_point.y), upper_bound(matched_point.y)).
    """

    def __init__(
            self,
            lower_bound: Optional[Union[Callable[[int], int], int]],
            upper_bound: Optional[Union[Callable[[int], int], int]],
            *args,
            **kwargs
    ) -> None:
        """
        :param lower_bound:
            Callable to compute the lower bound of the interval of admissible y values,
            relative to the currently matched point.
        :param upper_bound:
            Callable to compute the upper bound of the interval of admissible y values,
            relative to the currently matched point.
        """
        super().__init__(*args, **kwargs)
        self._lower_bound = lower_bound
        self._upper_bound = upper_bound

    def __call__(self, matched_point: Point, candidate_points: List[Point]) -> Generator[Point, None, None]:
        y = matched_point[1]
        lower_bound = None
        if self._lower_bound:
            lower_bound = self._lower_bound(y) if callable(self._lower_bound) else y + self._lower_bound

        upper_bound = None
        if self._upper_bound:
            upper_bound = self._upper_bound(y) if callable(self._upper_bound) else y + self._upper_bound

        return (
            candidate_point
            for candidate_point in candidate_points
            if (lower_bound is None or lower_bound < candidate_point[1]) and (
                upper_bound is None or candidate_point[1] < upper_bound)
        )
