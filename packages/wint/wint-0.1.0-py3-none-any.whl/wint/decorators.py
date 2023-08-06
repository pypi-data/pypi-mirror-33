import inspect
import typing
from functools import wraps

from .container import container
from .descriptor import DependencyDescriptor


def autowired(container=container):
    def inner(smth):
        if inspect.isclass(smth):
            return wire_class(container)(smth)

        return wire_func(container)(smth)

    return inner


def wire_class(container=container):
    def inner(cls):

        annotations = typing.get_type_hints(cls)

        for attr, typ in annotations.items():
            setattr(cls, attr, DependencyDescriptor(typ, container))

        for method_name, method in inspect.getmembers(cls, inspect.isroutine):
            if method_name.startswith("__") and method_name.endswith("__"):
                continue

            wrapped_method = wire_func(container=container)(method)
            setattr(cls, method_name, wrapped_method)

        return cls

    return inner


def wire_func(container=container):
    def inner(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            sig = inspect.signature(fn)
            if inspect.ismethod(fn):
                ba = sig.bind_partial(*args[1:], **kwargs)
            else:
                ba = sig.bind_partial(*args, **kwargs)

            for par_name, par in sig.parameters.items():
                if par_name not in ba.arguments and par.annotation:
                    a = container.resolve(par.annotation)
                    if a != container.EMPTY:
                        ba.arguments[par_name] = a

            return fn(*ba.args, **ba.kwargs)

        return wrapper

    return inner
