# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['apistar_crud']

package_data = \
{'': ['*']}

install_requires = \
['apistar>=0.5.30,<0.6.0']

setup_kwargs = {
    'name': 'apistar-crud',
    'version': '0.3.1',
    'description': 'API Star tools to create CRUD resources.',
    'long_description': '# API Star CRUD\n[![Build Status](https://travis-ci.org/PeRDy/apistar-crud.svg?branch=master)](https://travis-ci.org/PeRDy/apistar-crud)\n[![codecov](https://codecov.io/gh/PeRDy/apistar-crud/branch/master/graph/badge.svg)](https://codecov.io/gh/PeRDy/apistar-crud)\n[![PyPI version](https://badge.fury.io/py/apistar-crud.svg)](https://badge.fury.io/py/apistar-crud)\n\n* **Version:** :Version: * **Version:** 0.3.1\n* **Status:** Production/Stable\n* **Author:** José Antonio Perdiguero López\n\n## Features\nSupported **ORM**:\n* [SQLAlchemy](https://www.sqlalchemy.org/) through [apistar-sqlalchemy](https://github.com/PeRDy/apistar-sqlalchemy).\n* [Peewee](https://github.com/coleifer/peewee) through [apistar-peewee-orm](https://github.com/PeRDy/apistar-peewee-orm).\n\nThe resources are classes with a default implementation for **methods**:\n* `create`: Create a new element for this resource.\n* `retrieve`: Retrieve an element of this resource.\n* `update`: Update (partially or fully) an element of this resource.\n* `delete`: Delete an element of this resource.\n* `list`: List resource collection.\n* `drop`: Drop resource collection.\n\n----\n\nThe **routes** for these methods are:\n\n|Method  |Verb  |URL\n|--------|------|--------------\n|create  |POST  |/\n|retrieve|GET   |/{element_id}/\n|update  |PUT   |/{element_id}/\n|delete  |DELETE|/{element_id}/\n|list    |GET   |/\n|drop    |DELETE|/\n\n## Quick start\nInstall API star CRUD:\n\n```bash\n$ pip install apistar-crud[peewee]\n```\n\nor \n\n```\n$ pip install apistar-crud[sqlalchemy]\n```\n\nFollow the steps:\n\n1. Create an **input type** and **output type** for your resource:\n2. Define a **model** based on your ORM.\n3. Build your **resource** using the metaclass specific for your ORM.\n4. Add the **routes** for your resource.\n\n### SQLAlchemy\nExample of a fully functional resource based on SQLAlchemy.\n\nCreate an **input type** and **output type**:\n\n```python\nclass PuppyInputType(types.Type):\n    name = validators.String()\n\nclass PuppyOutputType(types.Type):\n    id = validators.Integer()\n    name = validators.String()\n```\n\nDefine a **model**:\n\n```python\nclass PuppyModel(Base):\n    __tablename__ = "Puppy"\n\n    id = Column(Integer, primary_key=True)\n    name = Column(String)\n```\n\nThe **resource**:\n\n```python\nfrom apistar_crud.sqlalchemy import Resource\n\nclass PuppyResource(metaclass=Resource):\n    model = PuppyModel\n    input_type = PuppyInputType\n    output_type = PuppyOutputType\n    methods = ("create", "retrieve", "update", "delete", "list", "drop")\n```\n\nThe resource generates his own **routes**:\n\n```python\nfrom apistar import Include\n\nroutes = [\n    Include("/puppy", "Puppy", PuppyResource.routes),\n]\n```\n\n### Peewee\nExample of a fully functional resource based on Peewee.\n\nCreate an **input type** and **output type**:\n\n```python\nclass PuppyInputType(types.Type):\n    name = validators.String()\n\nclass PuppyOutputType(types.Type):\n    id = validators.Integer()\n    name = validators.String()\n```\n\nDefine a **model**:\n\n```python\nclass PuppyModel(peewee.Model):\n    name = peewee.CharField()\n```\n\nThe **resource**:\n\n```python\nfrom apistar_crud.peewee import Resource\n\nclass PuppyResource(metaclass=Resource):\n    model = PuppyModel\n    input_type = PuppyInputType\n    output_type = PuppyOutputType\n    methods = ("create", "retrieve", "update", "delete", "list", "drop")\n```\n\nThe resource generates his own **routes**:\n\n```python\nfrom apistar import Include\n\nroutes = [\n    Include("/puppy", "Puppy", PuppyResource.routes),\n]\n```\n\n----\n\n### Override methods\n\nTo customize CRUD methods you can override them like:\n\n```python\nfrom apistar_crud.peewee import Resource\n\nclass PuppyResource(metaclass=Resource):\n    model = PuppyModel\n    input_type = PuppyInputType\n    output_type = PuppyOutputType\n    methods = ("create", "retrieve", "update", "delete", "list", "drop")\n    \n    @staticmethod\n    def create(element: PuppyInputType) -> PuppyOutputType:\n        # Do your custom process\n```\n',
    'author': 'José Antonio Perdiguero López',
    'author_email': 'perdy@perdy.io',
    'url': 'https://github.com/PeRDy/apistar-crud',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
