#!/usr/bin/env python
from distutils.core import setup, Command
import os
import re
import sys

from select_multiple_field import __version__


cmdclasses = dict()
README_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                           'README.rst')
long_description = open(README_PATH, 'r').read()


class DemoTester(Command):
    """Runs demonstration project tests"""

    user_options = []
    test_settings = {
        '1.4': 'test_projects.django14.django14.settings',
        '1.5': 'test_projects.django14.django14.settings',
        '1.6': 'test_projects.django14.django14.settings',
        '1.7': 'test_projects.django14.django14.settings',
    }

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        sys.dont_write_bytecode = True
        from django import get_version
        django_release = re.search(r'^\d\.\d', get_version()).group(0)
        if ((django_release not in self.test_settings.keys())
                or ([int(n) for n in re.split(r'[.ab]', get_version())]
                    < [1, 4, 2])):
            print("Please install Django 1.4.2 - 1.7 to run the test suite")
            exit(-1)
        os.environ['DJANGO_SETTINGS_MODULE'] = self.test_settings[
            django_release]
        try:
            from django.core.management import call_command
        except ImportError:
            print("Please install Django 1.4.2 - 1.7 to run the test suite")
            exit(-1)

        import django
        if hasattr(django, 'setup'):
            django.setup()

        call_command('test', 'pizzagigi', interactive=False, verbosity=1)
        call_command('test', 'forthewing', interactive=False, verbosity=1)

cmdclasses['test_demo'] = DemoTester


class Tester(Command):
    """Runs project unit tests"""

    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        sys.dont_write_bytecode = True
        os.environ['DJANGO_SETTINGS_MODULE'] = 'test_suite.settings_for_tests'
        import django
        if hasattr(django, 'setup'):
            django.setup()

        try:
            from django.utils.unittest import TextTestRunner, defaultTestLoader
        except ImportError:
            print("Please install Django => 1.4.2 to run the test suite")
            exit(-1)
        from test_suite import (
            test_codecs, test_forms, test_models, test_validators,
            test_widgets)
        suite = defaultTestLoader.loadTestsFromModule(test_codecs)
        suite.addTests(defaultTestLoader.loadTestsFromModule(test_forms))
        suite.addTests(defaultTestLoader.loadTestsFromModule(test_models))
        suite.addTests(defaultTestLoader.loadTestsFromModule(test_validators))
        suite.addTests(defaultTestLoader.loadTestsFromModule(test_widgets))
        runner = TextTestRunner()
        result = runner.run(suite)
        if result.wasSuccessful() is not True:
            raise SystemExit(int(bool(result.errors or result.failures)))

cmdclasses['test'] = Tester

setup(
    name='django-select-multiple-field',
    description='Select multiple choices in a single Django model field',
    long_description=long_description,
    version=__version__,
    license='BSD',
    keywords=[
        'select', 'select multiple', 'Django', 'model-field',
        'Django-Select-Multiple-Field'],
    author='Kelvin Wong',
    author_email='code@kelvinwong.ca',
    url='https://github.com/kelvinwong-ca/django-select-multiple-field',
    classifiers=['Development Status :: 3 - Alpha',
                 # 'Development Status :: 4 - Beta',
                 'Environment :: Web Environment',
                 'Framework :: Django',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: BSD License',
                 'Operating System :: OS Independent',
                 'Programming Language :: Python',
                 'Programming Language :: Python :: 2.6',
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 'Programming Language :: Python :: 3.2',
                 'Programming Language :: Python :: 3.3',
                 'Programming Language :: Python :: 3.4',
                 'Topic :: Internet :: WWW/HTTP'],
    packages=['select_multiple_field'],
    cmdclass=cmdclasses
)
