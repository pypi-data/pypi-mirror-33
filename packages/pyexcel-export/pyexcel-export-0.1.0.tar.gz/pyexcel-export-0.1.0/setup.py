# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['pyexcel_export']

package_data = \
{'': ['*']}

install_requires = \
['openpyxl>=2.5,<3.0', 'pyexcel-xlsx>=0.5.6,<0.6.0', 'pyexcel>=0.5.8,<0.6.0']

setup_kwargs = {
    'name': 'pyexcel-export',
    'version': '0.1.0',
    'description': 'Preserve good formatting when exporting to *.xlsx, *.ods, *.json and when updating data.',
    'long_description': '# pyexcel-export - Keep optimal formatting when exported to xlsx format\n\npyexcel-export is a wrapper around [pyexcel](https://github.com/pyexcel/pyexcel), [pyexcel-xlsx](https://github.com/pyexcel/pyexcel-xlsx) and [openpyxl](https://bitbucket.org/openpyxl/openpyxl) to read the formatting (stylesheets) and update the pre-existing file without destroying the stylesheets.\n\npyexcel-export also introduces a new exporting format, `*.pyexcel.json` which is based on [NoIndentEncoder](https://stackoverflow.com/a/25935321/9023855). This allows you to edit the spreadsheet in you favorite text editor, without being frustrated by automatically collapsed cells in Excel.\n\n## Known constraints\n\nThe "stylesheets" exported from Excel is in a very long base64 encoded format when exported to `*.json` or `*.pyexcel.json`, so exporting is disabled by default.\n\nAs stylesheets copying works by [`openpyxl.worksheet.copier.WorksheetCopy`](https://openpyxl.readthedocs.io/en/2.5/_modules/openpyxl/worksheet/copier.html), it may work only on values, styles, dimensions and merged cells, but charts might not be supported.\n\n## Installation\n\nYou can install pyexcel-export via pip:\n\n```commandline\n$ pip install pyexcel-export\n```\n\nor clone it and install it.\n\n## Usage\n\n### Exporting stylesheets\n\n```pydocstring\n>>> from pyexcel_export import get_stylesheet\n>>> get_stylesheet()\n{\n  "created": "\'2018-07-15T08:03:17.762214\'",\n  "has_header": "True",\n  "freeze_header": "True",\n  "col_width_fit_param_keys": "True",\n  "col_width_fit_ids": "True"\n}\n>>> get_stylesheet(\'test.xlsx\')\n{\n  "created": "\'2018-07-12T15:21:25.777499\'",\n  "modified": "\'2018-07-12T15:21:25.777523\'",\n  "has_header": "True",\n  "freeze_header": "True",\n  "col_width_fit_param_keys": "True",\n  "col_width_fit_ids": "True",\n  "_styles": "<_io.BytesIO object at 0x10553b678>"\n}\n```\n### Saving files, while preserving the formatting.\n```pydocstring\n>>> from pyexcel_export import get_stylesheet, save_data\n>>> stylesheet = get_stylesheet(\'test.xlsx\')\n>>> data = OrderedDict()\n>>> data.update({"Sheet 1": [["header A", "header B", "header C"], [1, 2, 3]]})\n>>> save_data("your_file.xlsx", data)\n```\n### \\*.pyexcel.json format\n```json\n{\n  "_meta": [\n    ["\\"created\\"", "\\"2018-07-12T15:21:25.777499\\""],\n    ["\\"modified\\"", "\\"2018-07-15T06:59:22.707162\\""],\n    ["\\"has_header\\"", "true"],\n    ["\\"freeze_header\\"", "true"],\n    ["\\"col_width_fit_param_keys\\"", "true"],\n    ["\\"col_width_fit_ids\\"", "true"]\n  ],\n  "test": [\n    ["\\"id\\"", "\\"English\\"", "\\"Pinyin\\"", "\\"Hanzi\\"", "\\"Audio\\"", "\\"Tags\\""],\n    ["1419644212689", "\\"Hello!\\"", "\\"Nǐ hǎo!\\"", "\\"你好！\\"", "\\"[sound:tmp1cctcn.mp3]\\"", "\\"\\""],\n    ["1419644212690", "\\"What are you saying?\\"", "\\"Nǐ shuō shénme?\\"", "\\"你说什么？\\"", "\\"[sound:tmp4tzxbu.mp3]\\"", "\\"\\""],\n    ["1419644212691", "\\"What did you do?\\"", "\\"nǐ zuò le shénme ?\\"", "\\"你做了什么？\\"", "\\"[sound:333012.mp3]\\"", "\\"\\""]\n  ]\n}\n```\n',
    'author': 'Pacharapol Withayasakpunt',
    'author_email': 'patarapolw@gmail.com',
    'url': 'https://github.com/patarapolw/pyexcel-export',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3',
}


setup(**setup_kwargs)
