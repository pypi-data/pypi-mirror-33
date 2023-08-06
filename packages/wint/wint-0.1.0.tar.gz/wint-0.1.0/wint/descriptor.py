from .container import container


class DependencyDescriptor:
    def __init__(self, typ, container=container):
        self.name = None
        self.typ = typ
        self.container = container

    def __get__(self, instance, owner):
        if self.name in instance.__dict__:
            return instance.__dict__[self.name]
        impl = self.container.resolve(self.typ)
        if impl == self.container.EMPTY:
            raise AttributeError()
        return impl

    def __set__(self, instance, value):
        instance.__dict__[self.name] = value

    def __set_name__(self, owner, name):
        self.name = name
