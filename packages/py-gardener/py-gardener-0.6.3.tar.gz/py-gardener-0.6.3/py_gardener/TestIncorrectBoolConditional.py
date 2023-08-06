import re
from py_gardener.InternalTestBase import InternalTestBase


class TestIncorrectBoolConditional(InternalTestBase):
    """
        Test asserts don't check 'in (True, False)' (false positives)
        Use `isinstance(val, bool)` instead
    """

    def test_incorrect_bool_conditional(self):
        assert_regex_compiled = re.compile(
            r'.*?\sin\s[\[(][^)\]]*?(True|False)[^)\]]*?[\])]'
        )
        matches = []
        for file_ in self.list_project_files():
            with open(file_, 'r') as f:
                for l in f.readlines():
                    match = assert_regex_compiled.match(l)
                    if match is not None:  # pragma: no cover
                        matches.append('%s: %s' % (
                            f.name.split('/')[-1], match.string.strip()))
        assert len(matches) == 0, 'Invalid assert(s):\n' + '\n'.join(matches)
