from django.contrib.auth.models import User
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Team, TournamentGroup
from .serializers import TeamSerializer, UserSerializer, TournamentGroupSerializer


class TeamListCreate(generics.ListCreateAPIView):
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Team.objects.all()

    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.save(author=self.request.user)
        else:
            print(serializer.errors)


class TeamDelete(generics.DestroyAPIView):
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Team.objects.all()


class CreateUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class TournamentGroupCreate(generics.CreateAPIView):
    serializer_class = TournamentGroupSerializer
    permission_classes = [IsAuthenticated]


class TournamentGroupBulkCreate(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        groups_data = request.data.get("groups", [])

        if not groups_data:
            raise ValidationError({"error": "No groups provided."})

        all_team_ids = [team_id for group in groups_data for team_id in group]
        if len(all_team_ids) != len(set(all_team_ids)):
            raise ValidationError({"error": "A team cannot be in multiple groups."})

        if len(all_team_ids) % 4 != 0:
            raise ValidationError({"error": "Teams must be grouped in multiples of 4."})

        if not 8 <= len(all_team_ids) <= 32:
            raise ValidationError(
                {"error": "Total number of teams must be between 8 and 32."}
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
            created_groups.append(TournamentGroupSerializer(group).data)

        return Response(created_groups, status=status.HTTP_201_CREATED)


class TournamentGroupDelete(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        TournamentGroup.objects.all().delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TournamentGroupList(generics.ListAPIView):
    serializer_class = TournamentGroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return TournamentGroup.objects.all()
