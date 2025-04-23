from itertools import combinations
from .models import Game


def generate_games_for_group(group):
    teams = group.teams.all()
    pairings = list(combinations(teams, 2))

    for team1, team2 in pairings:
        Game.objects.create(group=group, team1=team1, team2=team2)
