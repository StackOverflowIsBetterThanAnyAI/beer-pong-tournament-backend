from .models import Game, KnockoutGame, TournamentGroup


def all_group_games_played():
    return not Game.objects.filter(played=False).exists()


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


def get_group_standings():
    from collections import defaultdict

    group_standings = {}

    for group in TournamentGroup.objects.all():
        standings = defaultdict(
            lambda: {
                "team": None,
                "points": 0,
                "cups_scored": 0,
                "cups_conceded": 0,
            }
        )

        for game in group.games.filter(played=True):
            t1, t2 = game.team1, game.team2
            s1, s2 = game.score_team1, game.score_team2

            for team, scored, conceded in [(t1, s1, s2), (t2, s2, s1)]:
                stats = standings[team.id]
                stats["team"] = team
                stats["cups_scored"] += scored
                stats["cups_conceded"] += conceded
                if scored > conceded:
                    stats["points"] += 3
                elif scored == conceded:
                    stats["points"] += 1

        sorted_teams = sorted(
            standings.values(),
            key=lambda x: (
                -x["points"],
                -(x["cups_scored"] - x["cups_conceded"]),
                -x["cups_scored"],
            ),
        )
        group_standings[group.id] = sorted_teams

    return group_standings


def generate_knockout_stage():
    if not all_group_games_played():
        raise Exception("Not all group games have been played.")

    KnockoutGame.objects.all().delete()

    group_standings = get_group_standings()
    group_count = len(group_standings)
    teams_for_ko = []

    for standings in group_standings.values():
        teams_for_ko.extend([standings[0]["team"], standings[1]["team"]])

    if group_count in [3, 5, 6, 7]:
        third_place_teams = [s[2] for s in group_standings.values()]
        third_place_teams_sorted = sorted(
            third_place_teams,
            key=lambda x: (
                -x["points"],
                -(x["cups_scored"] - x["cups_conceded"]),
                -x["cups_scored"],
            ),
        )
        needed = {3: 2, 5: 2, 6: 4, 7: 2}[group_count]
        teams_for_ko.extend(t["team"] for t in third_place_teams_sorted[:needed])

    ko_team_count = len(teams_for_ko)
    if ko_team_count not in [4, 8, 16]:
        raise Exception(f"Invalid Knockout Stage team count: {ko_team_count}")

    round_code = {4: "SF", 8: "QF", 16: "R16"}[ko_team_count]

    matchups = []
    sorted_teams = teams_for_ko
    for i in range(ko_team_count // 2):
        team1 = sorted_teams[i]
        team2 = sorted_teams[-(i + 1)]
        matchups.append((team1, team2))

    for team1, team2 in matchups:
        KnockoutGame.objects.create(
            team1=team1,
            team2=team2,
            played=False,
            round=round_code,
        )
