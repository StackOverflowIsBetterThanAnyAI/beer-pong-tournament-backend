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
    path(
        "groups/standings/", views.GroupStandingsView.as_view(), name="group-standings"
    ),
    path(
        "ko-stage/",
        views.KnockoutGameListView.as_view(),
        name="list_knockout_games",
    ),
    path(
        "ko-stage/delete/",
        views.DeleteKnockoutStageView.as_view(),
        name="delete-ko-stage",
    ),
    path("ko-stage/<int:pk>/", views.UpdateKnockoutGameScoreView.as_view()),
    path(
        "ko-stage/generate/",
        views.GenerateKnockoutStageView.as_view(),
        name="generate-ko-stage",
    ),
    path(
        "ko-stage/next-round/",
        views.GenerateNextKnockoutRoundView.as_view(),
        name="generate-next-ko-round",
    ),
    path(
        "reset-tournament/",
        views.ResetTournamentView.as_view(),
        name="reset-tournament",
    ),
    path("me/", views.MeView.as_view(), name="me"),
    path("", include(router.urls)),
]
