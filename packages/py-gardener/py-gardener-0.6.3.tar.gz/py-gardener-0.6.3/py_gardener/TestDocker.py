import os
import pathlib
from shutil import copyfile
from py_gardener.InternalTestBase import InternalTestBase


class TestDocker(InternalTestBase):

    def test_docker(self):
        """ Test that tests are run inside a Docker container """
        if len(self.DOCKER) > 0:
            assert os.path.exists(os.path.join("/.dockerenv")), (
                'Please run in Docker using ". manage.sh"')

    def test_copy_docker_files(self):
        """ Test to copy lambda files into directory """
        if self.ROOT_DIR is None:
            return
        for type_ in self.DOCKER:
            base = os.path.join(
                os.path.dirname(__file__),
                "resources",
                "docker",
                type_
            )
            copyfile(
                os.path.join(base, 'manage.sh'),
                os.path.join(self.ROOT_DIR, 'manage.sh')
            )
            pathlib.Path(os.path.join(self.ROOT_DIR, 'docker')).mkdir(
                parents=True,
                exist_ok=True
            )
            copyfile(
                os.path.join(base, 'Dockerfile'),
                os.path.join(self.ROOT_DIR, 'docker', 'Dockerfile')
            )
