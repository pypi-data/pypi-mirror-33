# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['apistar_peewee_orm']

package_data = \
{'': ['*']}

install_requires = \
['apistar>=0.5.30,<0.6.0',
 'clinner>=1.9,<2.0',
 'peewee-migrate>=1.0,<2.0',
 'peewee>=3.5,<4.0']

entry_points = \
{'console_scripts': ['apistar-peewee-orm = apistar_peewee_orm.__main__:main']}

setup_kwargs = {
    'name': 'apistar-peewee-orm',
    'version': '0.2.1',
    'description': 'Peewee integration for API Star.',
    'long_description': '# API Star Peewee ORM\n[![Build Status](https://travis-ci.org/PeRDy/apistar-peewee-orm.svg?branch=master)](https://travis-ci.org/PeRDy/apistar-peewee-orm)\n[![codecov](https://codecov.io/gh/PeRDy/apistar-peewee-orm/branch/master/graph/badge.svg)](https://codecov.io/gh/PeRDy/apistar-peewee-orm)\n[![PyPI version](https://badge.fury.io/py/apistar-peewee-orm.svg)](https://badge.fury.io/py/apistar-peewee-orm)\n\n* **Version:** 0.2.1\n* **Status:** Production/Stable\n* **Author:** José Antonio Perdiguero López\n\nPeewee integration for API Star.\n\n## Features\nThis library provides:\n * Event hooks to handle **connections** and **commit/rollback** behavior based on exceptions in your views.\n * **Migrations** support with a command-line interface to interact with them.\n\n## Quick start\nInstall API Star Peewee ORM:\n\n```bash\npip install apistar-peewee-orm\n```\n\nCreate an API Star application adding components and event hooks:\n\n```python\nfrom apistar import App\nfrom apistar_peewee_orm import PeeweeDatabaseComponent, PeeweeTransactionHook\n\nroutes = []\n\ncomponents = [\n    PeeweeDatabaseComponent(url=\'sqlite://\'),\n]\n\nevent_hooks = [\n    PeeweeTransactionHook(),\n]\n\napp = App(routes=routes, components=components, event_hooks=event_hooks)\n```\n\nYour models now should inherit from a base model defined in this library:\n\n```python\nimport peewee\nfrom apistar_peewee_orm import Model\n\n\nclass PuppyModel(Model):\n    name = peewee.CharField()\n```\n\n## Full Example\n\n```python\nimport typing\n\nimport peewee\nfrom apistar import App, http, Route, types, validators\nfrom apistar_peewee_orm import Model, PeeweeDatabaseComponent, PeeweeTransactionHook\n\n\nclass PuppyModel(Model):\n    name = peewee.CharField()\n\n\nclass PuppyType(types.Type):\n    id = validators.Integer(allow_null=True, default=None)\n    name = validators.String()\n\n\ndef list_puppies() -> typing.List[PuppyType]:\n    return [PuppyType(puppy) for puppy in PuppyModel.select()]\n\n\ndef create_puppy(puppy: PuppyType, raise_exception: http.QueryParam) -> http.JSONResponse:\n    if raise_exception:\n        raise Exception\n\n    model = PuppyModel.create(**puppy)\n    return http.JSONResponse(PuppyType(model), status_code=201)\n\n\nroutes = [\n    Route(\'/puppy/\', \'POST\', create_puppy),\n    Route(\'/puppy/\', \'GET\', list_puppies),\n]\n\ncomponents = [\n    PeeweeDatabaseComponent(url=\'sqlite://\'),\n]\n\nevent_hooks = [\n    PeeweeTransactionHook(),\n]\n\napp = App(routes=routes, components=components, event_hooks=event_hooks)\n```\n\n## CLI Application\n\nAn application will be installed along with this library to provide full support for migrations and some other features \nof Peewee and API Star.\n\n```bash\n$ apistar-peewee-orm --help\n\nusage: apistar-peewee-orm [-h] [-s SETTINGS] [-q | -v] [--dry-run]\n                          {status,upgrade,downgrade,merge,create} ... [app]\n\npositional arguments:\n  app                   API Star application path\n                        (<package>.<module>:<variable>)\n\noptional arguments:\n  -h, --help            show this help message and exit\n  -s SETTINGS, --settings SETTINGS\n                        Module or object with Clinner settings in format\n                        "package.module[:Object]"\n  -q, --quiet           Quiet mode. No standard output other than executed\n                        application\n  -v, --verbose         Verbose level (This option is additive)\n  --dry-run             Dry run. Skip commands execution, useful to check\n                        which commands will be executed and execution order\n\nCommands:\n  {status,upgrade,downgrade,merge,create}\n    status              Database migrations and models status.\n    upgrade             Run database migrations sequentially.\n    downgrade           Rollback database migrations sequentially.\n    merge               Merge all migrations into a single one.\n    create              Create a new migration. If a module is provided then\n                        the migration will be automatically generated,\n                        otherwise the migration will be empty.\n```\n',
    'author': 'José Antonio Perdiguero López',
    'author_email': 'perdy@perdy.io',
    'url': 'https://github.com/PeRDy/apistar-peewee-orm',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
