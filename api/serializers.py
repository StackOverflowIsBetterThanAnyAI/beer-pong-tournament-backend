from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Game, Team, TournamentGroup


class GameSerializer(serializers.ModelSerializer):
    group = serializers.CharField(source="group.name", read_only=True)
    team1 = serializers.CharField(source="team1.name", read_only=True)
    team2 = serializers.CharField(source="team2.name", read_only=True)

    class Meta:
        model = Game
        fields = [
            "id",
            "group",
            "team1",
            "team2",
            "score_team1",
            "score_team2",
            "played",
        ]

    def validate(self, data):
        score1 = data.get("score_team1")
        score2 = data.get("score_team2")

        for score in [score1, score2]:
            if score is not None and (score < 0 or score > 10):
                raise serializers.ValidationError(
                    {"error": "Scores must be between 0 and 10."}
                )
        return data


class TeamSerializer(serializers.ModelSerializer):
    name = serializers.CharField(min_length=5, max_length=20)
    member_one = serializers.CharField(min_length=5, max_length=20)
    member_two = serializers.CharField(min_length=5, max_length=20)

    class Meta:
        model = Team
        fields = ["id", "name", "member_one", "member_two", "created_at"]

    def validate(self, data):
        if Team.objects.count() >= 32:
            raise serializers.ValidationError(
                {"error": "Maximum number of teams reached."}
            )

        name = data.get("name")
        member_one = data.get("member_one")
        member_two = data.get("member_two")

        if Team.objects.filter(name=name).exists():
            raise serializers.ValidationError(
                {"error": "This team name is already in use."}
            )

        if (
            Team.objects.filter(member_one=member_one).exists()
            or Team.objects.filter(member_two=member_one).exists()
        ):
            raise serializers.ValidationError(
                {"error": f"{member_one} is already part of a team."}
            )

        if (
            Team.objects.filter(member_one=member_two).exists()
            or Team.objects.filter(member_two=member_two).exists()
        ):
            raise serializers.ValidationError(
                {"error": f"{member_two} is already part of a team."}
            )

        if member_one == member_two:
            raise serializers.ValidationError(
                {"error": "Use two different members for a team."}
            )

        return data


class TeamStandingSerializer(serializers.Serializer):
    team = serializers.CharField()
    points = serializers.IntegerField()
    cups_scored = serializers.IntegerField()
    cups_conceded = serializers.IntegerField()
    cup_difference = serializers.IntegerField()
    played = serializers.IntegerField()


class StandingsSerializer(serializers.Serializer):
    group = serializers.CharField()
    standings = TeamStandingSerializer(many=True)


class TournamentGroupSerializer(serializers.ModelSerializer):
    teams = TeamSerializer(many=True, read_only=True)

    class Meta:
        model = TournamentGroup
        fields = ["id", "name", "teams", "created_at"]
        extra_kwargs = {"name": {"read_only": True}}

    def create(self, validated_data):
        teams = validated_data.pop("teams")
        group = TournamentGroup.objects.create(**validated_data)
        group.teams.set(teams)
        return group


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
