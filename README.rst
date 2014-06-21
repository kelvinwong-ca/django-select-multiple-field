****************************
django-select-multiple-field
****************************

Select multiple choices in a single Django model field. Use whenever you want
to store multiple choices in a field without using a many-to-many relation.

.. figure:: https://github.com/kelvinwong-ca/django-select-multiple-field/raw/master/docs/images/select_multiple_cropped.jpg

   Rendered using the multiselect.js plugin for jQuery [#]_

.. [#] jquery.multi-select.js https://github.com/lou/multi-select

Quick Start
===========

.. important::

    Field attribute ``max_length`` must be set to a value longer than your
    longest expected encoded string

In your models add the select field choices normally::

    # models.py

    class Pizza(models.Model):
        ANCHOVIES = 'a'
        BLACK_OLIVES = 'b'
        PEPPERONI = 'p'
        MOZZARELLA = 'm'
        TOPPING_CHOICES = (
            (ANCHOVIES, 'Anchovies'),
            (BLACK_OLIVES, 'Black olives'),
            (PEPPERONI, 'Pepperoni'),
            (MOZZARELLA, 'Mozzarella'),
        )

        toppings = SelectMultipleField(
            max_length=10,
            choices=TOPPING_CHOICES
        )

Use a generic view or a modelform as usual. In your template you can use a regular form tag::

    # template_form.html

    <form action="" method="post">
      {{ form.as_p  }}
      <input type="submit" value="Submit">
    </form>

This renders the following HTML::

    # create.html

    <form action="" method="post">
        <p>
          <label for="id_toppings">Toppings:</label>
          <select multiple="multiple" id="id_toppings" name="toppings"
              class="select-multiple-field">
            <option value="a">Anchovies</option>
            <option value="b">Black olives</option>
            <option value="p">Pepperoni</option>
            <option value="m">Mozzarella</option>
          </select>
        </p>
        <input type="submit" value="Submit">
    </form>

Displaying stored choices
-------------------------

To display your choices, you will need to decode the field contents. This can
be accomplished with a template tag::

    # templatetags/pizza_tags.py

    def decode_pie(ingredients):
        """
        Decode pizza pie toppings
        """
        decoder = dict(Pizza.TOPPING_CHOICES)
        decoded = [decoder[t] for t in ingredients]
        decoded.sort()
        return ', '.join(decoded)

    register.filter('decode_pie', decode_pie)

In your template you need to import your tags and use them::

    # details.html

    {% load pizza_tags %}

    {{ pizza.toppings|decode_pie }}

Encoding the choices
====================

The choices that are selected are stored as comma-delimited text. Consider a
pizza with the following toppings.

    * Pepperoni
    * Mozzarella

This would be stored as a character field as::

    p,m

This encoded string is decoded to a Python list using functions in the codecs
module::

    >>> from select_multiple_field.codecs import *
    >>> encoded = 'a,b,c'
    >>> decoded = decode_csv_to_list(encoded)
    >>> print decoded
    [u'a', u'b', u'c']
    >>> print type(decoded)
    <type 'list'>

The method of encoding may limit your ability to search for choices.

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
