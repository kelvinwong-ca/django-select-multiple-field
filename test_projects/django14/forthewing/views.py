# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse_lazy
from django.views.generic import (
    CreateView, DetailView, DeleteView, ListView, UpdateView)
from django.utils.encoding import force_text

from .models import ChickenWings


class ChickenWingsListView(ListView):

    queryset = ChickenWings.objects.order_by('-id')
    context_object_name = 'chickenwings'
    paginate_by = 10


class ChickenWingsCreateView(CreateView):

    model = ChickenWings
    fields = ['flavour']
    success_url = reverse_lazy('ftw:created')
    context_object_name = 'wings'


class ChickenWingsDetailView(DetailView):

    model = ChickenWings


class ChickenWingsUpdateView(UpdateView):

    model = ChickenWings
    fields = ['flavour']
    success_url = reverse_lazy('ftw:updated')


class ChickenWingsDeleteView(DeleteView):

    model = ChickenWings
    success_url = reverse_lazy('ftw:deleted')

    def get_success_url(self):
        return force_text(self.success_url)
