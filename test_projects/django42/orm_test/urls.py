from django.urls import path

from . import views

app_name = "orm"

urlpatterns = [
    path("", views.TaggedItemListView.as_view(), name="list"),
    path("create/", views.TaggedItemCreateView.as_view(), name="create"),
    path("<int:pk>/", views.TaggedItemDetailView.as_view(), name="detail"),
    path("<int:pk>/update/", views.TaggedItemUpdateView.as_view(), name="update"),
]