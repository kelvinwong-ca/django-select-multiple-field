# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from .migration_helpers import SouthMigrationTestCase

from .models import ChickenBalls


class MyMigrationTestCase(SouthMigrationTestCase):

    start_migration = '0001_initial'
    dest_migration = '0002_auto__add_field_chickenballs_dips'
    django_application = 'suthern'

    def test_field_survives_migration(self):
        self.migrate_to_dest()

        choice_1 = ChickenBalls.HONEY_MUSTARD
        order = ChickenBalls()
        order.dips = choice_1
        order.save()

        self.assertEqual(order.dips, [choice_1])
