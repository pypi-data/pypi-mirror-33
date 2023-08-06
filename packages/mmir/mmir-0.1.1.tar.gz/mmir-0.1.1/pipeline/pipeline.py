from funcy import rcompose


class Pipeline:
    def __init__(self, steps):
        self._steps = rcompose(*steps)

    def run(self, *args):
        return self._steps(*args)
