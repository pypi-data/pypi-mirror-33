import os
import sys
import shlex
import platform
import configparser
from os import PathLike
from typing import (
    Dict,
    Union,
    cast,
    List,
)
from threading import Thread
from subprocess import (
    Popen,
    PIPE,
)
from setuptools import Command


_RAISE = '___raise___'


class Cmd:  # pragma: no cover

    @staticmethod
    def _execute(command):
        def reader(stream, context):
            while True:
                line = stream.readline()
                if not line:
                    break
                else:
                    if context == "stderr":
                        print(line, end='', file=sys.stderr)
                    else:
                        print(line, end='')
        process = Popen(
            command,
            bufsize=-1,
            stdout=PIPE,
            stderr=PIPE,
            universal_newlines=True
        )
        thd1 = Thread(
            target=reader,
            args=(process.stdout, 'stdout')
        )
        thd1.start()
        thd2 = Thread(
            target=reader,
            args=(process.stderr, 'stderr')
        )
        thd2.start()
        process.wait()
        thd1.join()
        thd2.join()
        return process.returncode

    @classmethod
    def run(cls, *commands: str) -> int:
        for command in commands:
            command = cast(str, command)
            cmd: List[str] = shlex.split(command)
            print('-' * 80)
            print('%s' % ' '.join(cmd))
            code = cls._execute(cmd)
            if code != 0:
                print('exited with code: %s' % code)
                return code
        return 0


def _validate_setup_dir(setup_dir: Union[PathLike, str]) -> None:
    if not isinstance(setup_dir, str):
        raise TypeError(
            "The given 'setup_dir' must be a 'str' type.  Got: %r"
            % type(setup_dir).__name__
        )
    setup_dir = cast(str, setup_dir)
    setup_dir = setup_dir.strip()
    if not setup_dir:
        raise ValueError(
            "The given 'setup_dir' cannot be an empty string"
        )
    setup_dir = cast(PathLike, setup_dir)
    if not os.path.exists(setup_dir):
        raise ValueError(
            "The given 'setup_dir', %r,  is missing"
            % setup_dir
        )
    if not os.path.isdir(setup_dir):
        raise ValueError(
            "The given 'setup_dir', %r, is not a directory"
            % setup_dir
        )

    paths = (
        os.path.join(setup_dir, 'setup.cfg'),
        os.path.join(setup_dir, 'setup.py'),
    )
    for path in paths:
        if not os.path.isfile(path):
            raise ValueError(
                "The given 'setup_dir', %r, is invalid because it's missing "
                "the file: %r" % (setup_dir, path)
            )


class _SetupCfg(object):
    """Used to read values from a setup.cfg file"""

    def __init__(self, setup_dir: Union[PathLike, str]) -> None:
        self.cfg = configparser.ConfigParser()
        try:
            _validate_setup_dir(setup_dir)
        except ValueError:
            pass
        else:
            self.path = os.path.join(setup_dir, 'setup.cfg')
            self.cfg.read(self.path)

    def get(self, section, option, default=_RAISE):
        try:
            return self.cfg.get(section, option)
        except configparser.NoSectionError:
            if default != _RAISE:
                return default
            raise SystemExit(
                "%r is missing the '[%s]' section." % (self.path, section)
            )
        except configparser.NoOptionError:
            if default != _RAISE:
                return default
            raise SystemExit(
                "%r is missing %r in the '[%s]' section"
                % (self.path, option, section)
            )


class StyleCommand(Command):  # pragma: no cover

    root_path = ''
    description = 'check style consistency.'
    user_options: List = list()

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        sys.exit(Cmd.run('flake8 --count %s' % self.path))


def add_style_command_to_setup(
        setup_kwargs: Dict,
        setup_dir: Union[PathLike, str]
) -> None:
    cfg = _SetupCfg(setup_dir)
    name = cfg.get('metadata', 'name', default='').strip()
    if name:
        if 'cmdclass' not in setup_kwargs.keys():
            setup_kwargs['cmdclass'] = dict()

        StyleCommand.path = os.path.join(setup_dir, name)

        setup_kwargs['cmdclass']['style'] = StyleCommand


class LintCommand(Command):  # pragma: no cover

    root_path = ''
    description = 'parse code for errors.'
    user_options: List = list()

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        sys.exit(Cmd.run('pylint %s' % self.path))


def add_lint_command_to_setup(
        setup_kwargs: Dict,
        setup_dir: Union[PathLike, str]
) -> None:
    cfg = _SetupCfg(setup_dir)
    name = cfg.get('metadata', 'name', default='').strip()
    if name:
        if 'cmdclass' not in setup_kwargs.keys():
            setup_kwargs['cmdclass'] = dict()

        setup_kwargs['cmdclass']['lint'] = LintCommand

        LintCommand.path = os.path.join(setup_dir, name)


class PipelineTestsCommand(Command):  # pragma: no cover

    root_path = ''
    description = 'pipeline tests.'
    user_options: List = list()

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        commands = list()
        commands.append('pylint %s' % self.path)
        commands.append('flake8 --count %s' % self.path)
        commands.append('coverage run setup.py test')
        sys.exit(Cmd.run(*commands))


def add_pipeline_tests_command_to_setup(
        setup_kwargs: Dict,
        setup_dir: Union[PathLike, str]
) -> None:
    cfg = _SetupCfg(setup_dir)
    name = cfg.get('metadata', 'name', default='').strip()
    if name:
        if 'cmdclass' not in setup_kwargs.keys():
            setup_kwargs['cmdclass'] = dict()

        setup_kwargs['cmdclass']['pipelinetests'] = PipelineTestsCommand

        PipelineTestsCommand.path = os.path.join(setup_dir, name)


class CoverageCommand(Command):  # pragma: no cover

    root_path = ''
    description = 'run coverage on tests and show the coverage report.'
    user_options: List = list()

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        commands = list()
        commands.append('coverage run setup.py test')
        commands.append('coverage report')
        commands.append('coverage html')
        if self.path and platform.system() == 'Darwin':
            path = os.path.join(
                self.path,
                'htmlcov',
                'index.html'
            )
            commands.append("/usr/bin/open -a 'Google Chrome' %s" % path)
        sys.exit(Cmd.run(*commands))


def add_coverage_command_to_setup(
        setup_kwargs: Dict,
        setup_dir: Union[PathLike, str]
) -> None:
    cfg = _SetupCfg(setup_dir)
    test_suite = cfg.get('options', 'test_suite', default='').strip()
    if test_suite:
        if 'cmdclass' not in setup_kwargs.keys():
            setup_kwargs['cmdclass'] = dict()

        CoverageCommand.path = setup_dir

        setup_kwargs['cmdclass']['coverage'] = CoverageCommand
