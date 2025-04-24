from itertools import combinations
from .models import Game


def generate_games_for_group(group):
    teams = list(group.teams.all().order_by("name"))

    if len(teams) != 4:
        raise ValueError("One group does not contain four teams.")

    a, b, c, d = teams

    custom_order = [
        (a, b),
        (c, d),
        (a, c),
        (b, d),
        (d, a),
        (b, c),
    ]

    for pair in custom_order:
        Game.objects.create(group=group, team1=pair[0], team2=pair[1])
