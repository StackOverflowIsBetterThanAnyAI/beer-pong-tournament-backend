from collections import defaultdict
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Case, When, IntegerField
from rest_framework import generics, mixins, permissions, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Game, KnockoutGame, Team, TournamentGroup
from .serializers import (
    GameSerializer,
    KnockoutGameSerializer,
    TeamSerializer,
    TournamentGroupSerializer,
    UserSerializer,
)
from .permissions import IsAdminUser
from .utils import generate_games_for_group, generate_knockout_stage


class GameViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Game.objects.all().order_by("id")
    serializer_class = GameSerializer
    permission_classes = [IsAuthenticated]


class GenerateKnockoutStageView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        try:
            generate_knockout_stage()
            return Response(
                {"success": True, "message": "Knockout stage generated successfully."},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class KnockoutGameListView(ListAPIView):
    queryset = (
        KnockoutGame.objects.all()
        .annotate(
            round_order=Case(
                When(round="R16", then=1),
                When(round="QF", then=2),
                When(round="SF", then=3),
                When(round="F", then=4),
                default=99,
                output_field=IntegerField(),
            )
        )
        .order_by("round_order", "id")
    )
    serializer_class = KnockoutGameSerializer
    permission_classes = [IsAuthenticated]


class GroupStandingsView(APIView):
    def get(self, request):
        groups = TournamentGroup.objects.all()
        result = []

        for group in groups:
            standings = defaultdict(
                lambda: {
                    "team": "",
                    "points": 0,
                    "cups_scored": 0,
                    "cups_conceded": 0,
                    "cup_difference": "0",
                    "played": 0,
                }
            )

            teams_in_group = group.teams.all()
            for team in teams_in_group:
                standings[team.id]["team"] = team.name

            games = Game.objects.filter(group=group, played=True)

            for game in games:
                t1 = game.team1
                t2 = game.team2

                standings[t1.id]["cups_scored"] += game.score_team1
                standings[t1.id]["cups_conceded"] += game.score_team2
                standings[t1.id]["played"] += 1

                standings[t2.id]["cups_scored"] += game.score_team2
                standings[t2.id]["cups_conceded"] += game.score_team1
                standings[t2.id]["played"] += 1

                if game.score_team1 > game.score_team2:
                    standings[t1.id]["points"] += 3
                elif game.score_team1 < game.score_team2:
                    standings[t2.id]["points"] += 3
                else:
                    standings[t1.id]["points"] += 1
                    standings[t2.id]["points"] += 1

            formatted_standings = []

            for s in standings.values():
                cup_diff = s["cups_scored"] - s["cups_conceded"]

                if cup_diff > 0:
                    cup_diff_formatted = f"+{cup_diff}"
                else:
                    cup_diff_formatted = str(cup_diff)

                formatted_standings.append(
                    {
                        "team": s["team"],
                        "points": s["points"],
                        "cups_scored": s["cups_scored"],
                        "cups_conceded": s["cups_conceded"],
                        "cup_difference": cup_diff_formatted,
                        "played": s["played"],
                    }
                )

            group_data = {
                "group": group.name,
                "standings": sorted(
                    formatted_standings,
                    key=lambda x: (
                        -x["points"],
                        -int(x["cup_difference"].replace("+", "")),
                    ),
                ),
            }

            result.append(group_data)

        return Response(result, status=status.HTTP_200_OK)


class TeamListCreate(generics.ListCreateAPIView):
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Team.objects.all()

    def create(self, request, *args, **kwargs):
        from .models import Game

        if Game.objects.exists():
            return Response(
                {
                    "success": False,
                    "error": "Teams cannot be registered after the tournament has started.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {
                "success": True,
                "message": "Team created successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )


class TeamDelete(generics.DestroyAPIView):
    serializer_class = TeamSerializer
    permission_classes = [IsAdminUser, IsAuthenticated]

    def get_queryset(self):
        return Team.objects.all()

    def delete(self, request, *args, **kwargs):
        self.destroy(request, *args, **kwargs)
        return Response(
            {"success": True, "message": "Team deleted successfully."},
            status=status.HTTP_200_OK,
        )


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(
            {
                "success": True,
                "message": "User info fetched successfully.",
                "data": {"is_staff": user.is_staff},
            },
            status=status.HTTP_200_OK,
        )


class TournamentGroupCreate(generics.CreateAPIView):
    serializer_class = TournamentGroupSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response(
            {
                "success": True,
                "message": "Tournament group created successfully.",
                "data": response.data,
            },
            status=status.HTTP_201_CREATED,
        )


class TournamentGroupBulkCreate(APIView):
    permission_classes = [IsAdminUser, IsAuthenticated]

    def post(self, request):
        groups_data = request.data.get("groups", [])

        if not groups_data:
            raise ValidationError({"error": "No groups provided."})

        all_team_ids = [team_id for group in groups_data for team_id in group]
        if len(all_team_ids) != len(set(all_team_ids)):
            raise ValidationError({"error": "A team cannot be in multiple groups."})

        if len(all_team_ids) % 4 != 0:
            raise ValidationError({"error": "Teams must be grouped in multiples of 4."})

        if (
            not 8 <= len(all_team_ids) <= 32
            or len(all_team_ids) == 20
            or len(all_team_ids) % 4 != 0
        ):
            raise ValidationError(
                {"error": "Total number of teams must be between 8 and 32, but not 20."}
            )

        existing_teams = Team.objects.filter(id__in=all_team_ids)
        if existing_teams.count() != len(all_team_ids):
            raise ValidationError({"error": "One or more teams do not exist."})

        TournamentGroup.objects.all().delete()

        created_groups = []
        for index, team_ids in enumerate(groups_data, start=1):
            group = TournamentGroup.objects.create()
            teams = Team.objects.filter(id__in=team_ids)
            group.teams.set(teams)
            group.name = f"Group {index}"
            group.save()
            generate_games_for_group(group)
            created_groups.append(TournamentGroupSerializer(group).data)

        return Response(created_groups, status=status.HTTP_201_CREATED)


class TournamentGroupDelete(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        TournamentGroup.objects.all().delete()
        return Response(
            {"success": True, "message": "All tournament groups deleted."},
            status=status.HTTP_200_OK,
        )


class TournamentGroupList(generics.ListAPIView):
    serializer_class = TournamentGroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TournamentGroup.objects.all()

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "success": True,
                "message": "Groups fetched successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class UpdateKnockoutGameScoreView(APIView):
    def patch(self, request, pk):
        try:
            game = KnockoutGame.objects.get(pk=pk)
        except KnockoutGame.DoesNotExist:
            return Response(
                {"success": False, "error": "Game not found"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = KnockoutGameSerializer(game, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "success": True,
                    "message": "Score updated successfully.",
                    "data": serializer.data,
                }
            )
        return Response(
            {"success": False, "error": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class DeleteKnockoutStageView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        deleted_count, _ = KnockoutGame.objects.all().delete()
        return Response(
            {"success": True, "message": f"{deleted_count} knockout games deleted."},
            status=status.HTTP_200_OK,
        )


class GenerateNextKnockoutRoundView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        current = request.data.get("current_round")
        next_r = request.data.get("next_round")

        if not current or not next_r:
            return Response(
                {"error": "Both 'current_round' and 'next_round' are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            current_games = KnockoutGame.objects.filter(round=current, played=True)

            if current_games.count() % 2 != 0:
                raise Exception("Uneven number of games.")

            winners = []
            for game in current_games:
                if game.score_team1 > game.score_team2:
                    winners.append(game.team1)
                elif game.score_team2 > game.score_team1:
                    winners.append(game.team2)
                else:
                    raise Exception(f"Tied game in knockout stage: {game.id}")

            KnockoutGame.objects.filter(round=next_r).delete()

            for i in range(0, len(winners), 2):
                KnockoutGame.objects.create(
                    team1=winners[i],
                    team2=winners[i + 1],
                    round=next_r,
                )

            return Response(
                {
                    "success": True,
                    "message": f"{len(winners)//2} games created for round {next_r}.",
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {"success": False, "error": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )


class ResetTournamentView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        try:
            KnockoutGame.objects.all().delete()
            Game.objects.all().delete()
            TournamentGroup.objects.all().delete()
            Team.objects.all().delete()

            return Response(
                {"success": True, "message": "Tournament reset successful."},
                status=status.HTTP_200_OK,
            )
        except Exception as e:
            return Response(
                {"success": False, "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DeleteCypressTestUserView(APIView):
    permission_classes = [permissions.AllowAny]

    def delete(self, request):
        if not settings.DEBUG:
            return Response(
                {"error": "This endpoint is only available in DEBUG mode."},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            user = User.objects.get(username="CypressTestUser")
            user.delete()
            return Response({"success": True})
        except User.DoesNotExist:
            return Response(
                {"error": "CypressTestUser does not exist."},
                status=status.HTTP_204_NO_CONTENT,
            )
