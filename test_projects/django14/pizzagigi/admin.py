# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Pizza

class PizzaAdmin(admin.ModelAdmin):
    meu_model = Pizza
    list_display = ('get_toppings',)
    
    class Media:
        css = {
            'all': (
                '/static/multiselect-0.9.10/css/multi-select.css',
                '/static/css/style-multiselect.css',)
        }
        js = (
            'http://code.jquery.com/jquery-1.11.0.min.js',
            '/static/multiselect-0.9.10/js/jquery.multi-select.js',
            '/static/js/script-multiselect.js',
            )

admin.site.register(Pizza, PizzaAdmin)