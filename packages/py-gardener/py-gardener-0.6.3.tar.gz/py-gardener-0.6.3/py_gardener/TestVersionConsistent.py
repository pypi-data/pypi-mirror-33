import re
import os
import subprocess
from py_gardener.InternalTestBase import InternalTestBase


class TestVersionConsistent(InternalTestBase):
    """ Test setup.py version doesn't fall behind git tag. """

    def test_version_consistent(self):
        setup_path = os.path.join(self.ROOT_DIR, "setup.py")
        if os.path.isfile(setup_path):
            v1 = subprocess.check_output(
                'git describe --tags --abbrev=0'.split()
            ).strip().decode("utf-8")
            with open(setup_path) as f:
                v2 = re.search("version='([0-9.]+)',", f.read()).groups()[0]
            assert (
                list(map(int, v1.split("."))) <= list(map(int, v2.split(".")))
            )
