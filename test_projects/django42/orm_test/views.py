from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .models import TaggedItem


class TaggedItemListView(ListView):
    model = TaggedItem
    context_object_name = "items"
    paginate_by = 10


class TaggedItemCreateView(CreateView):
    model = TaggedItem
    fields = ["name", "tags", "category"]
    success_url = reverse_lazy("orm:list")


class TaggedItemDetailView(DetailView):
    model = TaggedItem


class TaggedItemUpdateView(UpdateView):
    model = TaggedItem
    fields = ["name", "tags", "category"]
    success_url = reverse_lazy("orm:list")