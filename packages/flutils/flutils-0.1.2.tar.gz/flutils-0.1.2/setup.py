#!/usr/bin/env python

import os
from setuptools import setup
from flutils import (
    add_coverage_command_to_setup,
    add_style_command_to_setup,
    add_lint_command_to_setup,
    add_pipeline_tests_command_to_setup,
)


setup_kwargs = dict()
setup_dir = os.path.dirname(os.path.realpath(__file__))
add_coverage_command_to_setup(setup_kwargs, setup_dir)
add_style_command_to_setup(setup_kwargs, setup_dir)
add_lint_command_to_setup(setup_kwargs, setup_dir)
add_pipeline_tests_command_to_setup(setup_kwargs, setup_dir)
setup(**setup_kwargs)
