from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DetailView,
    DeleteView,
    ListView,
    UpdateView,
)
from django.utils.encoding import force_str

from .models import Pizza


class PizzaListView(ListView):

    queryset = Pizza.objects.order_by("-id")
    context_object_name = "pizzas"
    paginate_by = 10


class PizzaCreateView(CreateView):

    model = Pizza
    fields = ["toppings", "dips"]
    success_url = reverse_lazy("pizza:created")


class PizzaDetailView(DetailView):

    model = Pizza


class PizzaUpdateView(UpdateView):

    model = Pizza
    fields = ["toppings", "dips"]
    success_url = reverse_lazy("pizza:updated")


class PizzaDeleteView(DeleteView):

    model = Pizza
    success_url = reverse_lazy("pizza:deleted")

    def get_success_url(self):
        return force_str(self.success_url)
