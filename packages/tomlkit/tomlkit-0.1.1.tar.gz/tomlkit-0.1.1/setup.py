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
    'version': '0.1.1',
    'description': 'Style preserving TOML library',
    'long_description': '# TOML Kit - Style-preserving TOML library for Python\n\nTOML Kit is a [TOML](https://github.com/toml-lang/toml) library.\n\nIt includes a parser that preserves all comments, indentations, whitespace and internal element ordering,\nand makes them accessible and editable via an intuitive API.\n\nYou can also create new TOML documents from scratch using the provided helpers.\n\n## Usage\n\n### Parsing\n\nTOML Kit comes with a fast and style-preserving parser to help you access\nthe content of TOML files and strings.\n\n```python\n>>> from tomlkit import dumps\n>>> from tomlkit import parse  # you can also use loads\n\n>>> content = """[table]\n... foo = "bar"  # String\n... """\n>>> doc = parse(content)\n\n# doc is a TOMLDocument instance that holds all the information\n# about the TOML string.\n# It behaves like a standard dictionary.\n\n>>> assert doc["table"]["foo"] == "bar"\n\n# The string generated from the document is exactly the same\n# as the original string\n>>> assert dumps(doc) == content\n```\n\n### Modifying\n\nTOML Kit provides an intuitive API to modify TOML documents.\n\n```python\n>>> from tomlkit import dumps\n>>> from tomlkit import parse\n>>> from tomlkit import table\n\n>>> doc = parse("""[table]\n... foo = "bar"  # String\n... """)\n\n>>> doc["table"]["baz"] = 13\n\n>>> dumps(doc)\n"""[table]\nfoo = "bar"  # String\nbaz = 13\n"""\n\n# Add a new table\n>>> tab = table()\n>>> tab.add("array", [1, 2, 3])\n\n>>> doc["table2"] = tab\n\n>>> dumps(doc)\n"""[table]\nfoo = "bar"  # String\nbaz = 13\n\n[table2]\narray = [1, 2, 3]\n"""\n\n# Remove the newly added table\n>>> doc.remove("table2")\n# del doc["table2] is also possible\n```\n\n### Writing\n\nYou can also write a new TOML document from scratch.\n\nLet\'s say we want to create this following document:\n\n```toml\n# This is a TOML document.\n\ntitle = "TOML Example"\n\n[owner]\nname = "Tom Preston-Werner"\norganization = "GitHub"\nbio = "GitHub Cofounder & CEO\\nLikes tater tots and beer."\ndob = 1979-05-27T07:32:00Z # First class dates? Why not?\n\n[database]\nserver = "192.168.1.1"\nports = [ 8001, 8001, 8002 ]\nconnection_max = 5000\nenabled = true\n```\n\nIt can be created with the following code:\n\n```python\n>>> from tomlkit import comment\n>>> from tomlkit import document\n>>> from tomlkit import nl\n>>> from tomlkit import table\n\n>>> doc = document()\n>>> doc.add(comment("This is a TOML document."))\n>>> doc.add(nl())\n>>> doc.add("title", "TOML Example")\n# Using doc["title"] = "TOML Example" is also possible\n\n>>> owner = table()\n>>> owner.add("name", "Tom Preston-Werner")\n>>> owner.add("organization", "GitHub")\n>>> owner.add("bio", "GitHub Cofounder & CEO\\\\nLikes tater tots and beer.")\n>>> dob = owner.add("dob", datetime(1979, 5, 27, 7, 32, tzinfo=utc))\n>>> dob.comment("First class dates? Why not?")\n\n# Adding the table to the document\n>>> doc.add("owner", owner)\n\n>>> atabase = table()\n>>> database["server"] = "192.168.1.1"\n>>> database["ports"] = [8001, 8001, 8002]\n>>> database["connection_max"] = 5000\n>>> database["enabled"] = True\n\n>>> doc["database"] = database\n```\n\n\n## Installation\n\nIf you are using [Poetry](https://poetry.eustace.io),\nadd `tomlkit` to your `pyproject.toml` file by using:\n\n```bash\npoetry add tomlkit\n```\n\nIf not, you can use `pip`:\n\n```bash\npip install tomlkit\n```\n',
    'author': 'Sébastien Eustace',
    'author_email': 'sebastien@eustace.io',
    'url': 'https://github.com/sdispater/tomlkit',
    'packages': packages,
    'package_data': package_data,
    'extras_require': extras_require,
    'python_requires': '>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
}


setup(**setup_kwargs)
