import math


class RangeObject:

    def __init__(self, s: int, e: int):
        self.start = s
        self.end = e
        self.step = 1

    @property
    def size(self) -> int:
        return int(math.fabs(self.start - self.end))
