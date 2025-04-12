from django.urls import path
from . import views

urlpatterns = [
    path("teams/", views.TeamListCreate.as_view(), name="team-list"),
    path("teams/delete/<int:pk>/", views.TeamDelete.as_view(), name="team-delete"),
]
