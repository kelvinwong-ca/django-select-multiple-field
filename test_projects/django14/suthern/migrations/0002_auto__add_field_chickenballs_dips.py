# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'ChickenBalls.dips'
        db.add_column('suthern_chickenballs', 'dips',
                      self.gf(u'select_multiple_field.models.SelectMultipleField')(default=u'', max_choices=3, include_blank=False, max_length=6, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'ChickenBalls.dips'
        db.delete_column('suthern_chickenballs', 'dips')


    models = {
        'suthern.chickenballs': {
            'Meta': {'object_name': 'ChickenBalls'},
            'dips': (u'select_multiple_field.models.SelectMultipleField', [], {'default': "u''", u'max_choices': 3, u'include_blank': False, 'max_length': '6', 'blank': 'True'}),
            'flavour': (u'select_multiple_field.models.SelectMultipleField', [], {u'max_choices': 2, u'include_blank': False, 'max_length': '5', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['suthern']