# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ChickenBalls'
        db.create_table('suthern_chickenballs', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('flavour', self.gf(u'select_multiple_field.models.SelectMultipleField')(max_choices=2, include_blank=False, max_length=5, blank=True)),
        ))
        db.send_create_signal('suthern', ['ChickenBalls'])


    def backwards(self, orm):
        # Deleting model 'ChickenBalls'
        db.delete_table('suthern_chickenballs')


    models = {
        'suthern.chickenballs': {
            'Meta': {'object_name': 'ChickenBalls'},
            'flavour': (u'select_multiple_field.models.SelectMultipleField', [], {u'max_choices': 2, u'include_blank': False, 'max_length': '5', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['suthern']