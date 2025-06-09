from typing import cast, Generic, TypeVar, Any

T = TypeVar('T')
class LazyObject(Generic[T]):
    def __init__(self, obj: T, root = None, attribute_chain: list[str] = None):
        self._root = root or obj
        self._obj = obj
        self._attribute_chain = attribute_chain or []
    def __getattr__(self, attribute: str) -> "LazyObject[Any]":
        attr = getattr(self._obj, attribute)
        return LazyObject(
            attr,
            root = self._root,
            attribute_chain = self._attribute_chain + [attribute])
    def evaluate_lazy_object(self) -> Any:
        attr = self._root
        for attribute_name in self._attribute_chain:
            attr = getattr(attr, attribute_name)
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
    def __new__(cls, name, bases, attrs, activators: list[str] = [], para_inits: list[str] = []):

        original_init = attrs['__init__']

        
        def lazy_init(self, *args, **kwargs):
            self._init_args = args
            self._init_kwargs = kwargs

            # Replace initializer with lazy initializer and calls to para-initializers
            evaluated_args, evaluated_kwargs = evaluate_lazy(args, kwargs)
            for init in para_inits:
                getattr(self, init)(*evaluated_args, **evaluated_kwargs)

        

        # Set activators to call initializer before they themselves are called
        attrs['_original_activator_methods'] = {
            activator: attrs[activator] for activator in activators
        }

        for activator in activators:
            activator_method = attrs[activator]
            def init_calling_activator(self, *args, _activator_method=activator_method, **kwargs):
                init_args, init_kwargs = evaluate_lazy(self._init_args, self._init_kwargs)
                del self._init_args, self._init_kwargs
                original_init(self, *init_args, **init_kwargs)

                # After the initialization occurs, return all activators to the methods that they were
                for activator, original_activator_method in self._original_activator_methods.items():
                    setattr(self, activator, original_activator_method)

                return _activator_method(self, *args, **kwargs)
            attrs[activator] = init_calling_activator

        
        attrs['__init__'] = lazy_init
        return super().__new__(cls, name, bases, attrs)

        