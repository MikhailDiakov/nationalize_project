from django.urls import path
from .views import NameStatView, PopularNamesView

urlpatterns = [
    path("names/", NameStatView.as_view(), name="name-stats"),
    path("popular-names/", PopularNamesView.as_view(), name="popular-names"),
]
