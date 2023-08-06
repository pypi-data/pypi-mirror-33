Wint - dependency injection with type hints.
============================================

Intro
-----

Wint is a lightweight library that implements dependency injection via type hinting.

This project is in development.

Documentation will come up later.


Examples
--------


```python
from wint import autowired, container


class Printer:
    def print(self, message):
        raise NotImplementedError


class RealPrinter(Printer):

    def print(self, message):
        print(message)


@autowired()
class PrintService:
    printer: Printer  # RealPrinter will be automatically injected as instance property

    def run(self, msg):
        self.printer.print(f"{msg}, i'm printing!")


if __name__ == "__main__":
    container.register(Printer, RealPrinter())  # register Printer implementation as singleton.

    PrintService().run('hey')
    >>> hey, i'm printing!

```
