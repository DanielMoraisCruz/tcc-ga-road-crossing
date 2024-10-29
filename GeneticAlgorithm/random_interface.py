from abc import ABC, abstractmethod


class RandomInterface(ABC):
    @abstractmethod
    def randint(self, a: int, b: int) -> int:
        pass

    @abstractmethod
    def random(self) -> float:
        pass

    @abstractmethod
    def choice(self, seq):
        pass
