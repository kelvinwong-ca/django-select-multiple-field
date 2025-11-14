#!/usr/bin/env python
import os
import re
import sys

from setuptools import Command, setup

REPO_BASE = os.path.abspath(os.path.dirname(__file__))


def get_version():
    """Read version without importing the package"""

    version_file = os.path.join(REPO_BASE, "select_multiple_field", "__init__.py")
    with open(version_file) as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip("'\"")
    raise RuntimeError("Unable to find version string.")


__version__ = get_version()


cmdclasses = dict()
README_PATH = os.path.join(REPO_BASE, "README.rst")
long_description = open(README_PATH, "r").read()


class DemoTester(Command):
    """Runs demonstration project tests"""

    user_options = []
    test_settings = {
        "4.2": "test_projects.django42.django42.settings",
        "5.2": "test_projects.django42.django42.settings",
    }

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        sys.dont_write_bytecode = True
        from django import get_version as django_get_version

        django_release = re.search(r"^\d\.\d+", django_get_version()).group(0)
        test_settings_exist = django_release in self.test_settings.keys()
        try:
            dj_ver = [int(n) for n in re.split(r"[.ab]", django_get_version())]
        except ValueError:
            # Pre-release Djangos must be testable!!!
            dj_too_old = False
        else:
            dj_too_old = dj_ver < [4, 2, 0]

        if test_settings_exist is False or dj_too_old:
            print("Please install Django 4.2.0 - 5.2 to run the test suite")
            exit(-1)
        os.environ["DJANGO_SETTINGS_MODULE"] = self.test_settings[django_release]

        import django

        if hasattr(django, "setup"):
            django.setup()

        from django.core.management import call_command

        call_command("test", "pizzagigi", interactive=False, verbosity=1)
        call_command("test", "forthewing", interactive=False, verbosity=1)


cmdclasses["test_demo"] = DemoTester


class Tester(Command):
    """Runs project unit tests"""

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        sys.dont_write_bytecode = True
        os.environ["DJANGO_SETTINGS_MODULE"] = "test_suite.settings_for_tests"
        import django

        if hasattr(django, "setup"):
            django.setup()

        from unittest import TextTestRunner, defaultTestLoader

        from test_suite import (
            test_codecs,
            test_forms,
            test_models,
            test_validators,
            test_widgets,
        )

        suite = defaultTestLoader.loadTestsFromModule(test_codecs)
        suite.addTests(defaultTestLoader.loadTestsFromModule(test_forms))
        suite.addTests(defaultTestLoader.loadTestsFromModule(test_models))
        suite.addTests(defaultTestLoader.loadTestsFromModule(test_validators))
        suite.addTests(defaultTestLoader.loadTestsFromModule(test_widgets))
        runner = TextTestRunner()
        result = runner.run(suite)
        if result.wasSuccessful() is not True:
            raise SystemExit(int(bool(result.errors or result.failures)))


cmdclasses["test"] = Tester

setup(
    name="django-select-multiple-field",
    description="Select multiple choices in a single Django model field",
    long_description=long_description,
    version=__version__,
    license="BSD",
    keywords=[
        "select",
        "select multiple",
        "Django",
        "model-field",
        "Django-Select-Multiple-Field",
    ],
    author="Kelvin Wong",
    author_email="code@kelvinwong.ca",
    url="https://github.com/kelvinwong-ca/django-select-multiple-field",
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Framework :: Django :: 4.2",
        "Framework :: Django :: 5.2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Topic :: Internet :: WWW/HTTP",
    ],
    packages=["select_multiple_field"],
    cmdclass=cmdclasses,
)
