from py_gardener.TestIncorrectBoolConditional import (
    TestIncorrectBoolConditional)
from py_gardener.TestLineEndings import TestLineEndings
from py_gardener.TestPep8 import TestPep8
from py_gardener.TestPylint import TestPylint
from py_gardener.TestStructure import TestStructure
from py_gardener.TestVersionConsistent import TestVersionConsistent
from py_gardener.TestDocker import TestDocker


class StaticTestBase(
    TestIncorrectBoolConditional,
    TestLineEndings,
    TestPep8,
    TestPylint,
    TestStructure,
    TestVersionConsistent,
    TestDocker
):
    pass
