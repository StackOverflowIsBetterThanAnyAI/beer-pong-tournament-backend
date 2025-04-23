from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r"games", views.GameViewSet, basename="games")

urlpatterns = [
    path("teams/", views.TeamListCreate.as_view(), name="team-list"),
    path("teams/delete/<int:pk>/", views.TeamDelete.as_view(), name="team-delete"),
    path("groups/", views.TournamentGroupList.as_view(), name="group-list"),
    path(
        "groups/bulk/",
        views.TournamentGroupBulkCreate.as_view(),
        name="group-bulk",
    ),
    path("groups/delete/", views.TournamentGroupDelete.as_view(), name="group-delete"),
    path("", include(router.urls)),
]
