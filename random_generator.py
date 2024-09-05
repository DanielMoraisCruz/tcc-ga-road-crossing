# random_generator.py
import random

from random_interface import RandomInterface


class RandomGenerator(RandomInterface):
    @staticmethod
    def randint(a: int, b: int) -> int:
        return random.randint(a, b)

    @staticmethod
    def random() -> float:
        return random.random()

    @staticmethod
    def choice(seq):
        return random.choice(seq)
