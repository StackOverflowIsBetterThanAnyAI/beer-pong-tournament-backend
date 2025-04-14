from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Team


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class TeamSerializer(serializers.ModelSerializer):
    name = serializers.CharField(min_length=5, max_length=20)
    member_one = serializers.CharField(min_length=5, max_length=20)
    member_two = serializers.CharField(min_length=5, max_length=20)

    class Meta:
        model = Team
        fields = ["id", "name", "member_one", "member_two", "created_at", "author"]
        extra_kwargs = {"author": {"read_only": True}}

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
