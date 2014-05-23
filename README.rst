****************************
django-select-multiple-field
****************************

Select multiple choices in a single Django model field.

.. warning::

    This Django module is not suitable for production use.

Sample application
==================

There is a sample application included if you downloaded the tarball. You can try it like this::

    $ pwd
    /home/user/teststuff/django-select-multiple-field
    $ cd test_projects/django14
    $ python manage.py syncdb
    $ python manage.py runserver

    Validating models...

    0 errors found
    Django version 1.4.2, using settings 'django14.settings'
    Development server is running at http://127.0.0.1:8000/
    Quit the server with CONTROL-C.

Troubleshooting
===============

Django-select-multiple-field contains two test suites. One is for the field and one is for an implementation of the field in a Django 1.4.2 project.

You can run the field tests by downloading the tarball and running 'test' in setup.py::

    $ python setup.py test

You can run the Django 1.4.2 demo test in a similar manner::

    $ python setup.py test_demo

Needless to say you will need to have Django 1.4.2 or later installed.

Bugs! Help!!
============

If you find any bugs in this software please report them via the Github
issue tracker [#]_ or send an email to code@kelvinwong.ca. Any serious
security bugs should be reported via email only.

.. [#] Django-select-multiple-field issue tracker https://github.com/kelvinwong-ca/django-select-multiple-field/issues

Links
=====

* https://pypi.python.org/pypi/django-select-multiple-field/
* https://github.com/kelvinwong-ca/django-select-multiple-field

Thank-you
=========

Thank-you for taking the time to evaluate this software. I appreciate
receiving feedback on your experiences using it and I welcome code
contributions and development ideas.

http://www.kelvinwong.ca/coders
