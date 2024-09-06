import random

from random_interface import RandomInterface


class RandomGenerator(RandomInterface):
    @classmethod
    def randint(cls, a: int, b: int) -> int:
        return random.randint(a, b)

    @classmethod
    def random(cls) -> float:
        return random.random()

    @classmethod
    def choice(cls, seq):
        return random.choice(seq)
