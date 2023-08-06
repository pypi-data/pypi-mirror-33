# -*- coding: utf-8 -*-
from distutils.core import setup

packages = \
['tomlkit']

package_data = \
{'': ['*']}

extras_require = \
{':(python_version >= "2.7" and python_version < "2.8") or (python_version >= "3.4" and python_version < "3.5")': ['typing>=3.6,<4.0'],
 ':python_version >= "2.7" and python_version < "2.8"': ['enum34>=1.1,<2.0']}

setup_kwargs = {
    'name': 'tomlkit',
    'version': '0.1.0',
    'description': 'Style preserving TOML library',
    'long_description': '# TOML Kit - Style-preserving TOML library for Python\n\nTOML Kit is a [TOML](https://github.com/toml-lang/toml) library.\n\nIt includes a parser that preserves all comments, indentations, whitespace and internal element ordering,\nand makes accessible and editable via an intuitive API.\n\nYou can also create a new TOML document from scratch using the provided helpers.\n\n## Usage\n\n### Parsing\n\nTOML Kit comes with a fast an style-preserving parser to help you access\nthe content of TOML files and strings.\n\n```python\nfrom tomlkit import dumps\nfrom tomlkit import parse  # you can also use loads\n\ncontent = """[table]\nfoo = "bar"  # String\n"""\ndoc = parse(content)\n\n# doc is a TOMLDocument instance that holds all the information\n# about the TOML string.\n# It behaves like a standard dictionary.\n\nassert doc["table"]["foo"] == "bar"\n\n# The string generated from the document is exactly the same\n# as the original string\nassert dumps(doc) == content\n```\n\n### Modifying\n\nTOML Kit provides an intuitive API to modify TOML documents.\n\n```python\nfrom tomlkit import dumps\nfrom tomlkit import parse\nfrom tomlkit import table\n\ndoc = parse("""[table]\nfoo = "bar"  # String\n""")\n\ndoc["table"]["baz"] = 13  # Setting element by keys is possible\n\ndumps(doc)\n"""[table]\nfoo = "bar"  # String\nbaz = 13\n"""\n\n# Add a new table\ntab = table()\ntab.add("array", [1, 2, 3])\n\ndoc["table2"] = tab\n\ndumps(doc)\n"""[table]\nfoo = "bar"  # String\nbaz = 13\n\n[table2]\narray = [1, 2, 3]\n"""\n\n# Remove the newly added table\ndoc.remove("table2")\n# del doc["table2] is also possible\n```\n\n### Writing\n\nYou can also write a new TOML document from scratch.\n\nLet\'s say we want to create this following document:\n\n```toml\n# This is a TOML document.\n\ntitle = "TOML Example"\n\n[owner]\nname = "Tom Preston-Werner"\norganization = "GitHub"\nbio = "GitHub Cofounder & CEO\\nLikes tater tots and beer."\ndob = 1979-05-27T07:32:00Z # First class dates? Why not?\n\n[database]\nserver = "192.168.1.1"\nports = [ 8001, 8001, 8002 ]\nconnection_max = 5000\nenabled = true\n```\n\nIt can be created with the following code:\n\n```python\nfrom tomlkit import comment\nfrom tomlkit import document\nfrom tomlkit import nl\nfrom tomlkit import table\n\ndoc = document()\ndoc.add(comment("This is a TOML document."))\ndoc.add(nl())\ndoc.add("title", "TOML Example")\n# Using doc["title"] = "TOML Example" is also possible\n\nowner = table()\nowner.add("name", "Tom Preston-Werner")\nowner.add("organization", "GitHub")\nowner.add("bio", "GitHub Cofounder & CEO\\\\nLikes tater tots and beer.")\ndob = owner.add("dob", datetime(1979, 5, 27, 7, 32, tzinfo=utc))\ndob.comment("First class dates? Why not?")\n\n# Adding the table to the document\ndoc.add("owner", owner)\n\ndatabase = table()\ndatabase["server"] = "192.168.1.1"\ndatabase["ports"] = [8001, 8001, 8002]\ndatabase["connection_max"] = 5000\ndatabase["enabled"] = True\n\ndoc["database"] = database\n```\n\n\n## Installation\n\nIf you are using [poetry](https://poetry.eustace.io),\nadd `tomlkit` to you `pyproject.toml` file by using:\n\n```bash\npoetry add tomlkit\n```\n\nIf not, you can use `pip`:\n\n```bash\npip install tomlkit\n```\n',
    'author': 'Sébastien Eustace',
    'author_email': 'sebastien@eustace.io',
    'url': 'https://github.com/sdispater/tomlkit',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
}


setup(**setup_kwargs)
