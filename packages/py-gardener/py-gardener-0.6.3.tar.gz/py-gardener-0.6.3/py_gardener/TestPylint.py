import os
import re
import multiprocessing
from multiprocessing.pool import ThreadPool
import time
from pylint import epylint
from py_gardener.InternalTestBase import InternalTestBase


class TestPylint(InternalTestBase):
    """ Test that we conform to Pylint. """

    def test_pylint(self):
        pool = ThreadPool(multiprocessing.cpu_count())
        files = []
        for file_ in self.list_project_files():
            rc_path = os.path.abspath(file_)
            while not os.path.isfile(os.path.join(rc_path, '.pylintrc')):
                assert rc_path != self.ROOT_DIR and rc_path != os.path.sep
                rc_path = os.path.abspath(rc_path + "/..")
            files.append([file_, rc_path])

        line_length = self.OPTIONS.get('max-line-length', 80)
        processes = [pool.apply_async(
            lambda f: epylint.py_run('%s --rcfile=%s --max-line-length=%s' % (
                f[0],
                os.path.join(f[1], ".pylintrc"),
                line_length
            ), return_std=True),
            [[file_path, rc_file_path]]
        ) for file_path, rc_file_path in files]

        while not all(p.ready() for p in processes):
            time.sleep(0.2)

        result = []
        for process in processes:
            stdout, stderr = map(lambda e: e.getvalue(), process.get())
            if "Your code has been rated at 10.00/10" not in stdout:
                for log in stdout.split("\n"):
                    if re.match(r"^\*{13} Module [a-zA-Z0-9._]+$", log):
                        continue
                    if re.match(r"^\s[-]+$", log):
                        continue
                    if re.match(
                        r"^\sYour code has been rated at \d+\.\d+/10 "
                        r"\(previous run: \d+\.\d+/10, [+\-]\d+\.\d+\)$",
                        log
                    ):
                        continue
                    if re.match(r"^\s*$", log):
                        continue
                    result.append(log.strip())
            if not re.match(
                r"^Using config file [/A-Za-z0-9\-_]+?\.pylintrc\n$",
                stderr
            ):
                result.append(stderr)
        pool.close()

        if len(result) > 0:
            for log in result:
                print(log)
            print("PyLint Problems: %s" % len(result))
        assert len(result) == 0
