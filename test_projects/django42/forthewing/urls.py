from django.urls import path
from django.views.generic import TemplateView

from .views import (
    ChickenWingsCreateView,
    ChickenWingsDeleteView,
    ChickenWingsDetailView,
    ChickenWingsListView,
    ChickenWingsUpdateView,
)

app_name = "ftw"

urlpatterns = [
    path("", ChickenWingsListView.as_view(), name="list"),
    path("create/", ChickenWingsCreateView.as_view(), name="create"),
    path(
        "created/",
        TemplateView.as_view(template_name="forthewing/chickenwings_created.html"),
        name="created",
    ),
    path("detail/<int:pk>/", ChickenWingsDetailView.as_view(), name="detail"),
    path("update/<int:pk>/", ChickenWingsUpdateView.as_view(), name="update"),
    path(
        "updated/",
        TemplateView.as_view(template_name="forthewing/chickenwings_updated.html"),
        name="updated",
    ),
    path("delete/<int:pk>/", ChickenWingsDeleteView.as_view(), name="delete"),
    path(
        "deleted/",
        TemplateView.as_view(template_name="forthewing/chickenwings_deleted.html"),
        name="deleted",
    ),
]
