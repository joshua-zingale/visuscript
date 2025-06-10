from typing import cast, Generic, TypeVar, Any, Tuple
from functools import cached_property
from types import MethodType

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
    
    def __call__(self, *args: Any, **kwargs: Any) -> "LazyObject[Any]":
        calls = self._calls.copy()
        calls[self._level] = (args, kwargs)
        return LazyObject(
            self._obj,
            _attribute_chain = self._attribute_chain,
            _calls = calls
            )
    def __getattr__(self, attribute: str) -> "LazyObject[Any]":
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

class LazyInitMetaClass(type):
    def __new__(meta, name, bases, attrs, activators: list[str] = [], para_inits: list[str] = []):
        cls = super().__new__(meta, name, bases, attrs)
        original_init = cls.__init__

        
        def lazy_init(self, *args, **kwargs):
            self._init_args = args
            self._init_kwargs = kwargs

            # Replace initializer with lazy initializer and calls to para-initializers
            evaluated_args, evaluated_kwargs = evaluate_lazy(args, kwargs)
            for init in para_inits:
                getattr(self, init)(*evaluated_args, **evaluated_kwargs)

        cls.__init__ = lazy_init
        

        # Set activators to call initializer before they themselves are called
        cls._original_activator_methods = {
            activator: attrs[activator] for activator in activators
        }

        for activator in activators:
            activator_method = getattr(cls, activator)
            def init_calling_activator(self, *args, _activator_method=activator_method, **kwargs):
                init_args, init_kwargs = evaluate_lazy(self._init_args, self._init_kwargs)
                del self._init_args, self._init_kwargs
                original_init(self, *init_args, **init_kwargs)

                # After the initialization occurs, return all activators to the methods that they were
                for activator, original_activator_method in self._original_activator_methods.items():
                    setattr(self, activator, MethodType(original_activator_method, self))

                return _activator_method(self, *args, **kwargs)
            setattr(cls, activator, init_calling_activator)
        return cls