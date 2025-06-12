from typing import cast, Generic, TypeVar, Any, Tuple, Self
from functools import cached_property


T = TypeVar('T')
class LazyObject(Generic[T]):
    def __init__(self,
                 obj: T,
                 _attribute_chain: list[str] = None,
                 _calls: dict[int, Tuple[Tuple[Any,...], dict[str, Any]]] = None):
        self._obj = obj
        self._attribute_chain = _attribute_chain or []
        self._calls = _calls or dict()
    
    @cached_property
    def _level(self) -> int:
        return len(self._attribute_chain)
    
    def __call__(self, *args: Any, **kwargs: Any) -> Self:
        calls = self._calls.copy()
        calls[self._level] = (args, kwargs)
        return LazyObject(
            self._obj,
            _attribute_chain = self._attribute_chain,
            _calls = calls
            )
    def __getattr__(self, attribute: str) -> Self:
        return LazyObject(
            self._obj,
            _attribute_chain = self._attribute_chain + [attribute],
            _calls = self._calls
            )
    
    def _lazy_call(self, obj, index: int):
        args, kwargs = self._calls[index]
        return obj(*args, **kwargs)
        
    def evaluate_lazy_object(self) -> Any:
        attr = self._obj
        for i, attribute_name in enumerate(self._attribute_chain):
            if i in self._calls:
                attr = self._lazy_call(attr, i)
            attr = getattr(attr, attribute_name)
        if self._level in self._calls:
            attr = self._lazy_call(attr, self._level)
        return attr
    
def evaluate_lazy(args: list[Any], kwargs: list[Any]):
    """Runs through arguments and keyword arguments and returns a new set
    with any LazyObjects having been evaluated."""
    new_args = []
    for arg in args:
        if isinstance(arg, LazyObject):
            new_args.append(arg.evaluate_lazy_object())
        else:
            new_args.append(arg)
    new_kwargs = dict()
    for key, value in kwargs.items():
        if isinstance(value, LazyObject):
            new_kwargs[key] = value.evaluate_lazy_object()
        else:
            new_kwargs[key] = value

    return new_args, new_kwargs
    
class Lazible:
    @property
    def lazy(self) -> Self:
        """Returns a :class:`LazyObject` for this object.

        To help with type-related hints in code editors,
        this function "lies" by claiming to return the type of Self.

        :return: A :class:`LazyObject` that wraps self.
        :rtype: LazyObject[Self]
        """        
        return cast(Self, LazyObject(self))