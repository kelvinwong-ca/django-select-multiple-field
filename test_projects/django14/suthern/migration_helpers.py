# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.management import call_command
from django.test import TransactionTestCase

from south.migration import Migrations


class SouthMigrationTestCase(TransactionTestCase):
    """A Test case for testing South migrations."""

    # Source:
    # https://micknelson.wordpress.com/2013/03/01/testing-django-migrations/

    # These must be defined by subclasses.
    start_migration = None
    dest_migration = None
    django_application = None

    def setUp(self):
        super(SouthMigrationTestCase, self).setUp()
        migrations = Migrations(self.django_application)
        self.start_orm = migrations[self.start_migration].orm()
        self.dest_orm = migrations[self.dest_migration].orm()

        # Ensure the migration history is up-to-date with a fake migration.
        # The other option would be to use the south setting for these tests
        # so that the migrations are used to setup the test db.
        call_command('migrate', self.django_application, fake=True,
                     verbosity=0)
        # Then migrate back to the start migration.
        call_command('migrate', self.django_application, self.start_migration,
                     verbosity=0)

    def tearDown(self):
        # Leave the db in the final state so that the test runner doesn't
        # error when truncating the database.
        call_command('migrate', self.django_application, verbosity=0)

    def migrate_to_dest(self):
        call_command('migrate', self.django_application, self.dest_migration,
                     verbosity=0)
