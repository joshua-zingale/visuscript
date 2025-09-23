from typing import cast, Any, Tuple, Self, TypeVar
from functools import cached_property


class LazyObject:
    def __init__(
        self,
        obj: Any,
        _attribute_chain: list[str] | None = None,
        _calls: dict[int, Tuple[Tuple[Any, ...], dict[str, Any]]] | None = None,
    ):
        self._obj = obj
        self._attribute_chain = _attribute_chain or []
        self._calls = _calls or dict()

    @cached_property
    def _level(self) -> int:
        return len(self._attribute_chain)

    def __call__(self, *args: Any, **kwargs: Any) -> "LazyObject":
        calls = self._calls.copy()
        calls[self._level] = (args, kwargs)
        return LazyObject(
            self._obj, _attribute_chain=self._attribute_chain, _calls=calls
        )

    def __getattr__(self, attribute: str) -> "LazyObject":
        return LazyObject(
            self._obj,
            _attribute_chain=self._attribute_chain + [attribute],
            _calls=self._calls,
        )

    def __add__(self, other: Any) -> "LazyObject":
        return self.__getattr__("__add__")(other)

    def __radd__(self, other: Any) -> "LazyObject":
        return self.__getattr__("__radd__")(other)

    def __sub__(self, other: Any) -> "LazyObject":
        return self.__getattr__("__sub__")(other)

    def __rsub__(self, other: Any) -> "LazyObject":
        return self.__getattr__("__rsub__")(other)

    def __mul__(self, other: Any) -> "LazyObject":
        return self.__getattr__("__mul__")(other)

    def __rmul__(self, other: Any) -> "LazyObject":
        return self.__getattr__("__rmul__")(other)

    def __truediv__(self, other: Any) -> "LazyObject":
        return self.__getattr__("__truediv__")(other)

    def __rtruediv__(self, other: Any) -> "LazyObject":
        return self.__getattr__("__rtruediv__")(other)

    def __neg__(self) -> "LazyObject":
        return self.__getattr__("__neg__")()

    def __pos__(self) -> "LazyObject":
        return self.__getattr__("__pos__")()

    def __abs__(self) -> "LazyObject":
        return self.__getattr__("__abs__")()

    def __invert__(self) -> "LazyObject":
        return self.__getattr__("__invert__")()

    def __getitem__(self, key: Any) -> "LazyObject":
        return self.__getattr__("__getitem__")(key)

    def __setitem__(self, key: Any, value: Any) -> None:
        raise NotImplementedError("LazyObject does not support item assignment.")

    def _lazy_call(self, obj: Any, index: int):
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


def evaluate_lazy(args: list[Any], kwargs: dict[str, Any]):
    """Runs through arguments and keyword arguments and returns a new set
    with any LazyObjects having been evaluated."""
    new_args: list[Any] = []
    for arg in args:
        if isinstance(arg, LazyObject):
            new_args.append(evaluate_lazy_object_or_tuple(arg))
        else:
            new_args.append(arg)
    new_kwargs: dict[str, Any] = dict()
    for key, value in kwargs.items():
        if isinstance(value, LazyObject):
            new_kwargs[key] = evaluate_lazy_object_or_tuple(value)
        else:
            new_kwargs[key] = value

    return new_args, new_kwargs

def evaluate_lazy_object_or_tuple(obj: LazyObject | tuple[Any, ...] | Any) -> tuple[Any, ...] | Any:
    """Evaluates a lazy object and returns the result.
    If the object is a tuple, constructs a new tuple by evaluating all
    lazy objects in the tuple and leaving all other objects the same.
    
    Leaves all other objects the same.
    """
    if isinstance(obj, LazyObject):
        return obj.evaluate_lazy_object()
    elif isinstance(obj, tuple):
        return tuple(map(evaluate_lazy_object_or_tuple, obj)) # type: ignore
    else:
        return obj



_T = TypeVar("_T")
def make_lazy(obj: _T) -> _T:
    """Returns a :class:`LazyObject` for an object
    
    To help with type-related hints in code editors,
    this function "lies" by claiming to return the type
    of the argument.
    """
    return cast(_T, LazyObject(obj))


class Lazible:
    @property
    def lazy(self) -> Self:
        """Returns a :class:`LazyObject` for this object.

        To help with type-related hints in code editors,
        this function "lies" by claiming to return the type of Self.

        :return: A :class:`LazyObject` that wraps self.
        """
        return cast(Self, LazyObject(self))
