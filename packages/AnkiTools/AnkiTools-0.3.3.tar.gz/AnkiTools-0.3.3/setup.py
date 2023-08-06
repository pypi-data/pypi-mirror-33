# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['ankitools', 'ankitools.api', 'ankitools.tools']

package_data = \
{'': ['*']}

install_requires = \
['appdirs>=1.4,<2.0',
 'bs4>=0.0.1,<0.0.2',
 'openpyxl>=2.5,<3.0',
 'psutil>=5.4,<6.0',
 'requests>=2.19,<3.0']

setup_kwargs = {
    'name': 'ankitools',
    'version': '0.3.3',
    'description': 'an Anki *.apkg and collection.anki2 reader and editor',
    'long_description': '# AnkiTools\n\n[![Build Status](https://travis-ci.org/patarapolw/AnkiTools.svg?branch=master)](https://travis-ci.org/patarapolw/AnkiTools)\n[![PyPI version shields.io](https://img.shields.io/pypi/v/AnkiTools.svg)](https://pypi.python.org/pypi/AnkiTools/)\n[![PyPI license](https://img.shields.io/pypi/l/AnkiTools.svg)](https://pypi.python.org/pypi/AnkiTools/)\n[![PyPI pyversions](https://img.shields.io/pypi/pyversions/AnkiTools.svg)](https://pypi.python.org/pypi/AnkiTools/)\n\nAn Anki *.apkg and collection.anki2 reader and editor to work with in Python. Also included a module on [AnkiConnect](https://github.com/FooSoft/anki-connect).\n\nI also created a new sync system called AnkiDirect.\n\nThe \\*.apkg format specification can be viewed from [Anki decks collaboration Wiki](http://decks.wikia.com/wiki/Anki_APKG_format_documentation) and [AnkiDroid](https://github.com/ankidroid/Anki-Android/wiki/Database-Structure). In my AnkiDirect, I tried to comply with the format specification as much as possible.\n\n## Installation\n\n```commandline\npip install AnkiTools\n```\n\n## Featured modules\n\n### Anki file conversion\n\n```pydocstring\n>>> from AnkiTools import anki_convert\n>>> anki_convert(\'Chinese.apkg\', out_file=\'Chinese_anki.xlsx\')\n>>> anki_convert(\'my_workbook.xlsx\', out_format=\'.apkg\')\n```\n\nThe supported formats are `.xlsx`, `.apkg` and `.anki2`.\n\n### AnkiDirect API\n\nYou can directly edit the Anki app data in user\'s Application Data path.\n\n```python\nfrom AnkiTools import AnkiDirect\nimport json\n\nwith open(\'payload.json\') as f:\n    payload = json.load(f)\nwith AnkiDirect() as api\n    api.add(payload)\n```\n\nSome supported payloads include:\n\n```json\n{\n  "data": {\n    "note_type A": [\n      {\n        "data": {\n          "header A": "a",\n          "header B": "b"\n        },\n        "decks": {\n          "Forward": "Test Deck::Forward",\n          "Backward": "Test Deck::Backward"\n        }\n      }\n    ]\n  },\n  "definitions": {\n    "note_type A": {\n      "templates": [\n        {\n          "name": "Forward",\n          "data": {\n            "qfmt": "{{header A}}",\n            "afmt": "{{FrontSide}}\\r\\n\\r\\n<hr id=answer>\\r\\n\\r\\n{{header B}}"\n          }\n        },\n        {\n          "name": "Backward",\n          "data": {\n            "qfmt": "{{header B}}",\n            "afmt": "{{FrontSide}}\\r\\n\\r\\n<hr id=answer>\\r\\n\\r\\n{{header A}}"\n          }\n        }\n      ],\n      "css": ".card {\\r\\n font-family: arial;\\r\\n font-size: 20px;\\r\\n text-align: center;\\r\\n color: black;\\r\\n background-color: white;\\r\\n}\\r\\n"\n    }\n  }\n}\n```\n\n### AnkiConnect\n\n```pydocstring\n>>> from AnkiTools import AnkiConnect\n>>> AnkiConnect.is_online()\nTrue\n>>> params = {\'actions\': [{\'action\': \'deckNames\'}, {\'action\': \'browse\', \'params\': {\'query\': \'deck:current\'}}]}\n>>> AnkiConnect.post(\'multi\', params=params)\n{\'result\': [[\'Default\', \'SpoonFed\', \'Chinese Hanzi Freq\', \'Chinese Vocab\'], None], \'error\': None}\n```\nThe actual addable actions and parameters can be viewed from [AnkiConnect](https://foosoft.net/projects/anki-connect/).\n\n## Plans\n\n- AnkiDirect two-way sync between Excel file and the Anki app.\n- Specifying metadata (e.g. card distribution, decks) in the Excel file and make it convertible and syncable.\n- Add CRUD to `AnkiDirect` ("update" and "remove" pending.)\n\n## Contributions\n\n- Testing on other OS\'s, e.g. Windows XP, Windows 10, Ubuntu Linux. (I tested on Mac.)\n- Manual testing of whether the generated `*.apkg` can be opened without subsequent errors in the Anki app.\n- Writing test cases and testing parameters. The current ones are viewable at [tests/parameters.json](https://github.com/patarapolw/AnkiTools/blob/master/tests/parameters.json) and [tests/files/](https://github.com/patarapolw/AnkiTools/tree/master/tests/files).\n- Specifying challenging payloads for AnkiDirect.\n',
    'author': 'Pacharapol Withayasakpunt',
    'author_email': 'patarapolw@gmail.com',
    'url': 'https://github.com/patarapolw/AnkiTools',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.5',
}


setup(**setup_kwargs)
