from django.urls import path
from django.views.generic import TemplateView

from .views import (
    PizzaCreateView,
    PizzaDeleteView,
    PizzaDetailView,
    PizzaListView,
    PizzaUpdateView,
)

app_name = "pizza"

urlpatterns = [
    path("", PizzaListView.as_view(), name="list"),
    path("create/", PizzaCreateView.as_view(), name="create"),
    path(
        "created/",
        TemplateView.as_view(template_name="pizzagigi/pizza_created.html"),
        name="created",
    ),
    path("detail/<int:pk>/", PizzaDetailView.as_view(), name="detail"),
    path("update/<int:pk>/", PizzaUpdateView.as_view(), name="update"),
    path(
        "updated/",
        TemplateView.as_view(template_name="pizzagigi/pizza_updated.html"),
        name="updated",
    ),
    path("delete/<int:pk>/", PizzaDeleteView.as_view(), name="delete"),
    path(
        "deleted/",
        TemplateView.as_view(template_name="pizzagigi/pizza_deleted.html"),
        name="deleted",
    ),
]
