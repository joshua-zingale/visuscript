from abc import ABC, abstractmethod
from typing import Callable, Generator
from functools import cached_property

# TODO Track when the invalidatable should be deallocated
class Invalidatable:
    @abstractmethod
    def _invalidate(self):
        """To be called whenever an Invalidator being observed sends its signal."""
        ...
        
class Invalidator:
    @abstractmethod
    def _iter_invalidatables(self) -> Generator[Invalidatable]:
        ...
    @abstractmethod
    def _add_invalidatable(self, invalidatable: Invalidatable):
        """Adds an :class :`Invalidatable` to this Invalidator."""
        ...

def invalidates(method):
    def invalidating_foo(self: Invalidator, *args, **kwargs):
        for invalidatable in self._iter_invalidatables():
            invalidatable._invalidate()
        return method(self, *args, **kwargs)
    return invalidating_foo


    # def _remove(self, invalidatable: Invalidatable):
    #     """Adds an :class :`Invalidatable` to this Invalidator."""
    #     ...


# def invalidateable_property(self, invalidator: Invalidator):
#     def invalidateable_property(property: Callable):
#         pass

    
