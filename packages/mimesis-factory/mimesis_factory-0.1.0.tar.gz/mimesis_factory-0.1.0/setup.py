# -*- coding: utf-8 -*-
from distutils.core import setup

install_requires = \
['factory-boy>=2.10', 'mimesis>=2.0']

setup_kwargs = {
    'name': 'mimesis-factory',
    'version': '0.1.0',
    'description': 'Mimesis integration with factory_boy',
    'long_description': '## mimesis_factory\n\n[![Build Status](https://travis-ci.org/mimesis-lab/mimesis-factory.svg?branch=master)](https://travis-ci.org/mimesis-lab/mimesis-factory)\n[![Coverage](https://coveralls.io/repos/github/mimesis-lab/mimesis-factory/badge.svg?branch=master)](https://coveralls.io/github/mimesis-lab/mimesis-factory?branch=master)\n[![Python](https://img.shields.io/badge/python-3.5%2C%203.6-brightgreen.svg)](https://badge.fury.io/py/mimesis)\n[![PyPI version](https://badge.fury.io/py/mimesis-factory.svg)](https://badge.fury.io/py/mimesis-factory)\n\n<a href="https://github.com/mimesis-lab/mimesis-factory">\n    <p align="center">\n        <img src="/media/logo.png">\n    </p>\n</a>\n\n\n## Description\n\nMimesis integration for [`factory_boy`](https://github.com/FactoryBoy/factory_boy).\n\n## Installation\n\n```python\n➜  pip install mimesis_factory\n```\n\n\n## Usage\n\nLook at the example below and you’ll understand how it works:\n\n```python\nclass Account(object):\n    def __init__(self, username, email, name, surname, age):\n        self.username = username\n        self.email = email\n        self.name = name\n        self.surname = surname\n        self.age = age\n```\n\nNow, use the `MimesisField` class from `mimesis_factory`\nto define how fake data is generated:\n\n```python\nimport factory\nfrom mimesis_factory import MimesisField\n\nfrom account import Account\n\nclass AccountFactory(factory.Factory):\n    class Meta:\n        model = Account\n        \n    username = MimesisField(\'username\', template=\'l_d\')\n    name = MimesisField(\'name\', gender=\'female\')\n    surname = MimesisField(\'surname\', gender=\'female\')\n    age = MimesisField(\'age\', minimum=18, maximum=90)\n    email = factory.LazyAttribute(\n        lambda o: \'%s@example.org\' % o.username\n    )\n    access_token = MimesisField(\'token\', entropy=32)\n```\n\n\n## pytest\n\nWe also recommend to use [`pytest-factoryboy`](https://github.com/pytest-dev/pytest-factoryboy).\nThis way it will be possible to integrate your factories into `pytest` fixtures.\n\n\n## License\n\nmimesis_factory is released under the MIT License.\n',
    'author': 'Nikita Sobolev',
    'author_email': 'mail@sobolevn.me',
    'url': 'https://github.com/mimesis-lab/mimesis-factory',
    'py_modules': 'mimesis_factory',
    'install_requires': install_requires,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
