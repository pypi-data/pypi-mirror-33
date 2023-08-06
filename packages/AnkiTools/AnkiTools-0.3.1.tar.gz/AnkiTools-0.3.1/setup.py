# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['ankitools', 'ankitools.tools']

package_data = \
{'': ['*']}

install_requires = \
['appdirs>=1.4,<2.0',
 'bs4>=0.0.1,<0.0.2',
 'openpyxl>=2.5,<3.0',
 'requests>=2.19,<3.0']

setup_kwargs = {
    'name': 'ankitools',
    'version': '0.3.1',
    'description': 'an Anki *.apkg and collection.anki2 reader and editor',
    'long_description': '# AnkiTools\n\n[![Build Status](https://travis-ci.org/patarapolw/AnkiTools.svg?branch=master)](https://travis-ci.org/patarapolw/AnkiTools)\n[![PyPI version shields.io](https://img.shields.io/pypi/v/AnkiTools.svg)](https://pypi.python.org/pypi/AnkiTools/)\n[![PyPI license](https://img.shields.io/pypi/l/AnkiTools.svg)](https://pypi.python.org/pypi/AnkiTools/)\n[![PyPI pyversions](https://img.shields.io/pypi/pyversions/AnkiTools.svg)](https://pypi.python.org/pypi/AnkiTools/)\n[![PyPI status](https://img.shields.io/pypi/status/AnkiTools.svg)](https://pypi.python.org/pypi/AnkiTools/)\n\nAn Anki *.apkg and collection.anki2 reader and editor to work with in Python. Also included a module on [AnkiConnect](https://github.com/FooSoft/anki-connect).\n\nI also created a new sync system called AnkiDirect.\n\nThe \\*.apkg format specification can be viewed from [Anki decks collaboration Wiki](http://decks.wikia.com/wiki/Anki_APKG_format_documentation) and [AnkiDroid](https://github.com/ankidroid/Anki-Android/wiki/Database-Structure). In my AnkiDirect, I tried to comply with the format specification as much as possible.\n\n## Installation\n\n```commandline\npip install AnkiTools\n```\n\n## Features\n\n- Read and write to Anki database in Application Data.\n- Read and create Anki file without Anki\n- Convert back and forth to Excel.\n\n# Examples\n\n```python\nimport json\nfrom collections import OrderedDict\n\nfrom AnkiTools import AnkiDirect\n\n\nif __name__ == \'__main__\':\n    with open(\'notes.json\') as f:\n        data = json.load(f, object_pairs_hook=OrderedDict)\n\n    api = AnkiDirect()\n    api.add(data)\n    api.conn.commit()\n```\nwhere `notes.json` is\n\n```json\n{\n  "data": {\n    "note_type A": [\n      {\n        "data": {\n          "header A": "a",\n          "header B": "b"\n        },\n        "decks": {\n          "Forward": "Test Deck::Forward",\n          "Backward": "Test Deck::Backward"\n        }\n      }\n    ]\n  },\n  "definitions": {\n    "note_type A": {\n      "templates": [\n        {\n          "name": "Forward",\n          "data": {\n            "qfmt": "{{header A}}",\n            "afmt": "{{FrontSide}}\\r\\n\\r\\n<hr id=answer>\\r\\n\\r\\n{{header B}}"\n          }\n        },\n        {\n          "name": "Backward",\n          "data": {\n            "qfmt": "{{header B}}",\n            "afmt": "{{FrontSide}}\\r\\n\\r\\n<hr id=answer>\\r\\n\\r\\n{{header A}}"\n          }\n        }\n      ],\n      "css": "This is a test css."\n    }\n  }\n}\n```\n',
    'author': 'Pacharapol Withayasakpunt',
    'author_email': 'patarapolw@gmail.com',
    'url': 'https://ankitools.readthedocs.io/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5',
}


setup(**setup_kwargs)
