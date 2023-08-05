# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pipis']

package_data = \
{'': ['*']}

install_requires = \
['click>=6.7,<7.0', 'tabulate>=0.8,<0.9']

entry_points = \
{'console_scripts': ['pipis = pipis:cli']}

setup_kwargs = {
    'name': 'pipis',
    'version': '1.5.0',
    'description': 'Wraps pip and venv to install scripts',
    'long_description': '# PIPIS\n\n| **tests** | [![pipeline status](https://gitlab.com/NicolasKAROLAK/pipis/badges/master/pipeline.svg)](https://gitlab.com/NicolasKAROLAK/pipis/commits/master) [![coverage report](https://gitlab.com/NicolasKAROLAK/pipis/badges/master/coverage.svg)](https://gitlab.com/NicolasKAROLAK/pipis/commits/master) |\n|-|-|\n| **package** | [![PyPI version](https://img.shields.io/pypi/v/pipis.svg)](https://pypi.org/project/pipis) [![Supported versions](https://img.shields.io/pypi/pyversions/pipis.svg)](https://pypi.org/project/pipis) [![PyPI - Status](https://img.shields.io/pypi/status/pipis.svg)](https://gitlab.com/NicolasKAROLAK/pipis) |\n\n## Somewhere between pip and pipsi\n\n> "pipis" stands for "pip isolate" \\\n> and "pipi" is the french for "peepee" which is a fun name but [pipi](https://pypi.org/project/pipi/) was already taken…\n\nActually it is a rewrite of [pipsi](https://github.com/mitsuhiko/pipsi) but with [venv](https://docs.python.org/dev/library/venv.html) instead of [virtualenv](https://virtualenv.pypa.io/en/stable/).\n\n## What does it do?\n\nPipis is a wrapper around venv and pip which installs scripts provided by python packages into separate venvs to shield them from your system and each other.\n\nIt creates a venv in `~/.local/venvs/`, update pip, installs the package, and links the package\'s scripts to `~/.local/bin/`. These directory can be changed respectively through the environment variables `PIPIS_VENVS` and `PIPIS_BIN`.\n\n## Why not pipsi?\n\nBecause i do not care about Python 2, and `virtualenv` copies python\'s binaries while `venv` just symlink them (which i think is cleaner, but it still copies `pip` which is not clean…).\n\n## How to install\n\n```\npython3 -m venv ~/.local/venvs/pipis\nsource ~/.local/venvs/pipis/bin/activate\npip install -U pip\npip install pipis\ndeactivate\nmkdir -p ~/.local/bin\nln -s ~/.local/venvs/pipis/bin/pipis ~/.local/bin/pipis\n```\n\n## How to update\n\n```\npipis update pipis\n```\n\n## How to uninstall\n\n```\npipis uninstall pipis\n```\n\n## How to use\n\n### Show help\n\n```\n$ pipis --help\nUsage: pipis [OPTIONS] COMMAND [ARGS]...\n\nOptions:\n  --help  Show this message and exit.\n\nCommands:\n  install\n  list\n  uninstall\n  update\n```\n\nYou can also invoke `--help` on each commands.\n\n### Install package(s)\n\n```\n$ pipis install ansible\nDo you want to continue? [y/N]: y\nInstalling  [####################################]  100%\n```\n\nYou can install multiple packages:\n\n```\n$ pipis install ansible ansible-lint jmespath\nDo you want to continue? [y/N]: y\nInstalling  [####################################]  100%\n```\n\n### Unattended install package(s)\n\n```\n$ pipis install --yes awscli\nInstalling  [####################################]  100%\n```\n\n### Update package(s)\n\n```\n$ pipis update ansible\nDo you want to continue? [y/N]: y\nUpdating  [####################################]  100%\n```\n\nYou can also update all installed packages at once:\n\n```\n$ pipis update\nDo you want to continue? [y/N]: y\nUpdating  [####################################]  100%\n```\n\n### List installed packages\n\n```\n$ pipis list\nInstalled:\n  - ansible\n  - ansible-lint\n  - awscli\n  - bashate\n  - docker-compose\n  - flake8\n  - jmespath\n  - pipis\n  - poetry\n  - pylint\n  - python-language-server\n  - twine\n```\n\n### Uninstall package(s)\n\n```\n$ pipis uninstall ansible\nDo you want to continue? [y/N]: y\nRemoving  [####################################]  100%\n```\n\n## Credits\n\n- [Armin Ronacher](https://github.com/mitsuhiko): the author of pipsi, for the inspiration\n- [Nicolas Karolak](): myself, the author of pipis\n',
    'author': 'Nicolas KAROLAK',
    'author_email': 'nicolas@karolak.fr',
    'url': 'https://gitlab.com/NicolasKAROLAK/pipis',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.4,<4.0',
}


setup(**setup_kwargs)
