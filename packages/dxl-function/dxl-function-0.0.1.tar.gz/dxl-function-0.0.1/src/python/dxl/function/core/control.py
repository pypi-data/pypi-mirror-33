from abc import ABCMeta, abstractmethod
from typing import Callable, Union, List, Tuple, Dict

__all__ = ['Functor', 'fmap', 'Applicative']

BuiltInFunctor = Union[List, Tuple, Dict]


class Functor(metaclass=ABCMeta):
    @abstractmethod
    def _inner(self):
        ...

    @abstractmethod
    def fmap(self, f):
        """
        Returns TypeOfFunctor(f(self.data)),
        mimics fmap :: (a -> b) -> a -> b by
        fmap( fa ) -> type(fmap)(f(a))
        """
        ...


FunctorB = Union[Functor, BuiltInFunctor]  # Functor and built-in "Functor"s


def fmap(f: Callable, fct: FunctorB) -> FunctorB:
    if isinstance(fct, Functor):
        return fct.fmap(f)
    if isinstance(fct, (list, tuple)):
        return type(fct)(map(f, fct))
    if isinstance(fct, dict):
        return {k: f(v) for k, v in fct.items()}


class Applicative(Functor, metaclass=ABCMeta):
    @abstractmethod
    def apply(self, x: Functor):
        ...

    def run(self):
        return self.fmap(lambda f: f())
