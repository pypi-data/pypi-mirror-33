from . import punq


class PunqContainer:
    EMPTY = "__EMPTY__"

    def __init__(self):
        self.container = punq.Container()

    def __str__(self):
        return f"<{self.__class__.__name__}>"

    def resolve(self, typ, *args, **kwargs):
        try:
            return self.container.resolve(typ, *args, **kwargs)
        except punq.MissingDependencyException:
            return self.EMPTY

    def register(self, typ, impl=None, **kwargs):
        return self.container.register(typ, impl, **kwargs)


container = PunqContainer()
