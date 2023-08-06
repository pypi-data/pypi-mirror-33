from typing import Callable

__all__ = ['Function', 'to']


class Function(Callable):
    pass


from abc import ABCMeta, abstractclassmethod


class Convertable(metaclass=ABCMeta):
    @abstractclassmethod
    def from_(cls, *args, **kwargs):
        ...


def to(o) -> Function:
    if isinstance(o, Convertable):
        return o.from_
    else:
        return type(o)
