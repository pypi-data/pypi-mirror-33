# newcli

Utility to create a new Python CLI.

## Quickstart

```bash
pipenv install newcli
newcli init
```

## Install

```bash
# Command(s)

pipenv install newcli
pip3 install --user newcli
```

## Commands

### `init`

```bash
# Command

newcli init
```

`newci` will then prompt you for basic information about your project!
The output creates this folder structure:

```bash
{{project}}/
├── LICENSE
├── MANIFEST.in
├── Pipfile
├── README.md
├── setup.py
├── tox.ini
└── {{project}}
    ├── __init__.py
    ├── __version__.py
    ├── cli.py
    └── core.py
```

## Template CLI Project

### Testing CLI

`cd` into the directory and install to your current virtualenv

```bash
# Command
pipenv isntall -e .
```

Now run the new tool!

```
{{project}}

Usage: {{project}} [OPTIONS] COMMAND [ARGS]...

  {{project}}

Options:
  --help  Show this message and exit.
```

Now you can begin adding new functions!

### Versioning

The project will be date versioned with as today's `YEAR.MONTH.DAY.SUBVERSION`. This handles most project updates great, and required the user to update the subversion manually in `__version__.py`.

### Publish to PyPy

-   Creating a new repository on [PyPi](https://pypi.org/) is quick and easy. Quickly build and upload a new project or update an existing one with:

```bash
# Command
python setup.py upload
```

## TODO

-   100% unit tests and run on TravisCI
-   populate GitHub information from .gitconfig
-   init a new GitHub repository
-   add .travis.yml configuration
-   add template tox configuration
-   add template test files and folder structure
-   add template README.md
-   ability to create, register, and share new templates
