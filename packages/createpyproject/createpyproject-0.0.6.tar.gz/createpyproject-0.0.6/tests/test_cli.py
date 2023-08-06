import os
import subprocess
import unittest
from click.testing import CliRunner

from createpy import cli

class CliTest(unittest.TestCase):

    def tearDown(self):
        # work_dir = os.sep.join(os.path.abspath(os.path.dirname(__file__)).split(os.sep)[:-1])
        cmd = ['rm', '-rf', 'test_project']
        subprocess.Popen(cmd).wait()

    def test_create(self):
        runner = CliRunner()
        result = runner.invoke(cli.main, ['create'])
        assert result.exit_code == 0
        assert 'test_project' in result.output 


if __name__ == '__main__':
    unitest.main()
