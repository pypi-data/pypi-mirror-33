from typing import Callable, Any


class Interceptor:
    """
    Utility class you can use to add in between pipeline steps for various operations like
    swapping data.

    Accepts an intercept function which will be called on the data
    which passes through the interceptor when the pipeline is executed
    """
    def __init__(self, intercept: Callable[[Any], Any]=None):
        self.intercept = intercept

    def __call__(self, *args, **kwargs):
        return self.intercept(*args, **kwargs)
