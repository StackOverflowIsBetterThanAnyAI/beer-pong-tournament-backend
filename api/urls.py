from django.urls import path
from . import views

urlpatterns = [
    path("teams/", views.TeamListCreate.as_view(), name="team-list"),
    path("teams/delete/<int:pk>/", views.TeamDelete.as_view(), name="team-delete"),
    path("groups/", views.TournamentGroupList.as_view(), name="group-list"),
    path(
        "groups/bulk/",
        views.TournamentGroupBulkCreate.as_view(),
        name="group-bulk-create",
    ),
]
