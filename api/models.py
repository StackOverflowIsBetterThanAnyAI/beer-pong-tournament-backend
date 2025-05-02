from django.db import models


class Game(models.Model):
    group = models.ForeignKey(
        "TournamentGroup", on_delete=models.CASCADE, related_name="games"
    )
    team1 = models.ForeignKey(
        "Team", on_delete=models.CASCADE, related_name="games_as_team1"
    )
    team2 = models.ForeignKey(
        "Team", on_delete=models.CASCADE, related_name="games_as_team2"
    )
    score_team1 = models.PositiveIntegerField(null=True, blank=True)
    score_team2 = models.PositiveIntegerField(null=True, blank=True)
    played = models.BooleanField(default=False)

    class Meta:
        unique_together = ("group", "team1", "team2")

    def __str__(self):
        return f"{self.team1} vs {self.team2} (Group {self.group.id})"


class Team(models.Model):
    name = models.CharField(max_length=20, unique=True)
    member_one = models.CharField(max_length=20, unique=True)
    member_two = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class TournamentGroup(models.Model):
    name = models.CharField(max_length=10, blank=True)
    teams = models.ManyToManyField(Team)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.name:
            existing_count = TournamentGroup.objects.count()
            self.name = f"Group {existing_count + 1}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class KnockoutGame(models.Model):
    ROUND_CHOICES = [
        ("R16", "Round of 16"),
        ("QF", "Quarter Final"),
        ("SF", "Semi Final"),
        ("F", "Grand Final"),
    ]

    team1 = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="ko_games_as_team1"
    )
    team2 = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name="ko_games_as_team2"
    )
    score_team1 = models.PositiveIntegerField(null=True, blank=True)
    score_team2 = models.PositiveIntegerField(null=True, blank=True)
    played = models.BooleanField(default=False)
    round = models.CharField(max_length=3, choices=ROUND_CHOICES)

    def __str__(self):
        return f"{self.get_round_display()}: {self.team1} vs {self.team2}"
