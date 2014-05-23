# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms import widgets
from django.forms.util import flatatt
from django.utils.safestring import mark_safe

try:
    from django.utils.html import format_html
except ImportError:
    def format_html(format_string, *args, **kwargs):
        return format_string.format(*args, **kwargs)


class SelectMultipleField(widgets.SelectMultiple):
    """Multiple select widget ready for jQuery multiselect.js"""

    allow_multiple_selected = True

    def render(self, name, value, attrs=None, choices=()):
        rendered_attrs = {'class': 'select-multiple-field'}
        rendered_attrs.update(attrs)
        if value is None:
            value = []

        final_attrs = self.build_attrs(rendered_attrs, name=name)
        # output = [u'<select multiple="multiple"%s>' % flatatt(final_attrs)]
        output = [format_html('<select multiple="multiple"{0}>',
                              flatatt(final_attrs))]
        options = self.render_options(choices, value)
        if options:
            output.append(options)

        output.append('</select>')
        return mark_safe('\n'.join(output))
