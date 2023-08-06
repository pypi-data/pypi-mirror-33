[![Build Status](https://img.shields.io/travis/loopmediagroup/py-gardener/master.svg)](https://travis-ci.org/loopmediagroup/py-gardener)
[![Coverage Status](https://coveralls.io/repos/github/loopmediagroup/py-gardener/badge.svg?branch=master)](https://coveralls.io/github/loopmediagroup/py-gardener?branch=master)
[![Dependencies](https://pyup.io/repos/github/loopmediagroup/py-gardener/shield.svg?t=1518818417448)](https://pyup.io)

# Py-Gardener

Released on [pypi](https://pypi.python.org/pypi/Py-Gardener). Install with

`pip install py-gardener`

### What is Py-Gardener?

Py-Gardener enforces best practices for your python project.

### Run Tests

Check out [SETUP.md](SETUP.md)

### Where can I get help?

Please open a github issue.

-------------------

## Getting Started

### How to Integrate


Copy the [example test file](tests/test_StaticTestBase.py) to the following folder with class `TestGardener`:

`$PROJECT_DIR/tests/static/test_gardener.py`

Fields:

`ROOT_DIR`: The root path of the project.

`TEST_DIR`: The test path of the project.

`LIB_DIR`: The source code of the project.

`DOCKER`: Optional list of Docker containers the project is developed against.

`EXCLUDE`: List of files to be not considered project files for test directory. Defaults to `["env"]`.

`OPTIONS`: General options specified below:

* `max-line-length`: Default 80, max line length for pylint and PEP8 rules.

### What are the tests?

#### Test Incorrect Bool Conditional

Test asserts don't check `val in (True, False)`. This can result in false positives when `val == 1 or val == 0`.

Use `isinstance(val, bool)` instead

Incorrect:

    >>> 0 in (True, False)
    True
    >>> 1 in (True, False)
    True

Correct:

    >>> isinstance(0, bool)
    False


#### Test Line Endings

Test that lines do not end with backslash - use parenthesis instead

Incorrect:
```python
assert 'key' in values or \
    condition is True
```

Correct:
```python
assert (
    'key' in values or
    condition is True
)
```

#### Test PEP8

Test that we conform to PEP8.

#### Test Pylint

Test that we conform to Pylint.

Pylint requires a config to adhere to. 

To generate the default config, run:

     $ pylint --generate-rcfile > .pylintrc

To add different configurations for sub-directories, include a separate `.pylintrc` at the root of the subdirectory.

Example: 

```
$PROJECT_ROOT
|-- Dir1
|    |-- file1.py
|-- Dir2
|    |-- Dir3
|    |    |-- file2.py
|    |-- file3.py
|    |-- .pylintrc
|-- .pylintrc
```

In the above scenario, `file1.py` would be validated against `$PROJECT_ROOT/.pylintrc` whereas `file2.py` & `file3.py` would be validated against `$PROJECT_ROOT/Dir2/.pylintrc`.

[PyLint Message Reference](http://pylint-messages.wikidot.com/all-codes)

#### Test Structure

##### Test Class Names Match

Test that test class names are correct. (Test class name must match file name)

For example:

`test_Example.py`
```python
import unittest


class TestExample(unittest.TestCase):
    ...
```

##### Test Related Lib File Exists

Check test files have corresponding `$LIB_DIR` file if folder exists.

Example:

`$TEST_DIR/dir/test_Example.py` requires `$LIB_DIR/dir/Example.py` if `$LIB_DIR/dir` exists.

##### Test Init Files Exist

Check that all sub folders in $TEST_DIR have an `__init__.py` file.

#### Test Version Consistent

*_Only validates if `$PROJECT_ROOT/setup.py` exists_*

Test setup.py version doesn't fall behind git tag.

#### Test Docker

*_Only validates if `DOCKER` (above) is not an empty list_*

Test that tests are run inside a Docker container.
