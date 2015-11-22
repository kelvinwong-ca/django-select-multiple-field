# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse_lazy
from django.views.generic import (
    CreateView, DetailView, DeleteView, ListView, UpdateView)
from django.utils.encoding import force_text

from .models import Pizza


class PizzaListView(ListView):

    queryset = Pizza.objects.order_by('-id')
    context_object_name = 'pizzas'
    paginate_by = 10


class PizzaCreateView(CreateView):

    model = Pizza
    fields = ['toppings']
    success_url = reverse_lazy('pizza:created')


class PizzaDetailView(DetailView):

    model = Pizza


class PizzaUpdateView(UpdateView):

    model = Pizza
    fields = ['toppings']
    success_url = reverse_lazy('pizza:updated')


class PizzaDeleteView(DeleteView):

    model = Pizza
    success_url = reverse_lazy('pizza:deleted')

    def get_success_url(self):
        return force_text(self.success_url)
