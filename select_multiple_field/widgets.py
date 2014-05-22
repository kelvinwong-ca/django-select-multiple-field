# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms import widgets
from django.forms.util import flatatt
from django.utils.safestring import mark_safe


class SelectMultipleField(widgets.SelectMultiple):
    """Multiple select widget ready for jQuery multiselect.js"""

    allow_multiple_selected = True

    def render(self, name, value, attrs=None, choices=()):
        rendered_attrs = {'class': 'select-multiple-field'}
        rendered_attrs.update(attrs)
        if value is None:
            value = []

        final_attrs = self.build_attrs(rendered_attrs, name=name)
        output = [u'<select multiple="multiple"%s>' % flatatt(final_attrs)]
        options = self.render_options(choices, value)
        if options:
            output.append(options)

        output.append('</select>')
        return mark_safe(u'\n'.join(output))
