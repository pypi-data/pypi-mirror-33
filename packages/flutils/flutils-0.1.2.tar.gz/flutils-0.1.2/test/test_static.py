import sys
import unittest
import warnings
from threading import Thread
from subprocess import Popen
from subprocess import PIPE
from io import StringIO


class Command:

    def __init__(self):
        self.stdout_cache = None
        self.stderr_cache = None

    def _execute(self, command):

        p = Popen(
            command,
            bufsize=-1,
            stdout=PIPE,
            stderr=PIPE,
            universal_newlines=True
        )
        t1 = Thread(
            target=self.reader,
            args=(p.stdout, 'stdout')
        )
        t1.start()
        t2 = Thread(
            target=self.reader,
            args=(p.stderr, 'stderr')
        )
        t2.start()
        p.wait()
        t1.join()
        t2.join()
        return p.returncode

    def reader(self, stream, context):
        while True:
            s = stream.readline()
            if not s:
                break
            else:
                if context == "stderr":
                    self.stderr_cache.write(s)
                else:
                    self.stdout_cache.write(s)

    @staticmethod
    def _to_lines(obj):
        lines = obj.getvalue()
        if isinstance(lines, bytes):
            lines = lines.encode(sys.getdefaultencoding())
        return list(map(lambda x: x.strip(), lines.splitlines()))

    def __call__(self, command):
        self.stdout_cache = StringIO()
        self.stderr_cache = StringIO()
        res = self._execute(command)
        out = self._to_lines(self.stdout_cache)
        out += self._to_lines(self.stderr_cache)
        self.stdout_cache.close()
        self.stderr_cache.close()
        out = '\n%s' % '\n'.join(out)
        return res, out

    @classmethod
    def run(cls, command):
        run = cls()
        return run(command)


class TestStaticTypes(unittest.TestCase):

    longMessage = False

    def setUp(self):
        self.cmd = [
            'mypy',
            '--ignore-missing-imports',
            '-p',
            'flutils'
        ]
        warnings.filterwarnings(
            action="ignore",
            message="unclosed",
            category=ResourceWarning
        )

    def test_static_types(self):
        """Static type checking with mypy"""
        res, txt = Command.run(self.cmd)
        if res != 0:
            txt = 'The following problems were found with mypy:\n%s' % txt
            self.fail(msg=txt)


