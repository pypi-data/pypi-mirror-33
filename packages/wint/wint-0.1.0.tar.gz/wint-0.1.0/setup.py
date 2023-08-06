# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['wint', 'wint.punq']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'wint',
    'version': '0.1.0',
    'description': 'Dependency injection with type hints',
    'long_description': 'Wint - dependency injection with type hints.\n============================================\n\nIntro\n-----\n\nWint is a lightweight library that implements dependency injection via type hinting.\n\nThis project is in development.\n\nDocumentation will come up later.\n\n\nExamples\n--------\n\n\n```python\nfrom wint import autowired, container\n\n\nclass Printer:\n    def print(self, message):\n        raise NotImplementedError\n\n\nclass RealPrinter(Printer):\n\n    def print(self, message):\n        print(message)\n\n\n@autowired()\nclass PrintService:\n    printer: Printer  # RealPrinter will be automatically injected as instance property\n\n    def run(self, msg):\n        self.printer.print(f"{msg}, i\'m printing!")\n\n\nif __name__ == "__main__":\n    container.register(Printer, RealPrinter())  # register Printer implementation as singleton.\n\n    PrintService().run(\'hey\')\n    >>> hey, i\'m printing!\n\n```\n',
    'author': 'Stanislav Lobanov',
    'author_email': 'n10101010@gmail.com',
    'url': 'https://github.com/asyncee/wint',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.6',
}


setup(**setup_kwargs)
