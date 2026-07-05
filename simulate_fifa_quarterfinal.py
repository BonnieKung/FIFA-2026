import csv
import random
from pathlib import Path

random.seed(42)

DATA_FILE = Path(__file__).with_name("FIFA.csv")


def load_teams(path: Path):
    with path.open(encoding="utf-8-sig") as f:
        lines = [line.strip() for line in f if line.strip()]

    if not lines:
        return []

    header = [item.strip() for item in lines[0].strip().strip('"').split(",")]
    teams = []
    for line in lines[1:]:
        values = [item.strip().strip('"') for item in line.strip().strip('"').split(",")]
        row = dict(zip(header, values))
        teams.append(
            {
                "Country": row["Country"].strip(),
                "Group Points": int(row["Group Points"]),
                "FIFA Ranking": int(row["FIFA Ranking"]),
                "Goals For (GF)": int(row["Goals For (GF)"]),
                "Goals Against (GA)": int(row["Goals Against (GA)"]),
                "Expected Goals (xG)": float(row["Expected Goals (xG)"]),
                "Yellow Cards": int(row["Yellow Cards"]),
                "Host Country": row["Host Country"].strip(),
            }
        )
    return teams


def team_strength(team):
    ranking = team["FIFA Ranking"]
    group_points = team["Group Points"]
    xg = team["Expected Goals (xG)"]
    gf = team["Goals For (GF)"]
    ga = team["Goals Against (GA)"]
    host_bonus = 20 if team["Host Country"].lower() == "yes" else 0
    return 1200 - ranking * 10 + group_points * 12 + xg * 15 + gf * 3 - ga * 4 + host_bonus


def simulate_match(team_a, team_b):
    rating_a = team_strength(team_a)
    rating_b = team_strength(team_b)

    attack_a = max(0.8, 1.0 + (rating_a - rating_b) / 700)
    attack_b = max(0.8, 1.0 + (rating_b - rating_a) / 700)

    goals_a = 0
    goals_b = 0

    for _ in range(2):
        if random.random() < 0.45 * attack_a:
            goals_a += 1
        if random.random() < 0.45 * attack_b:
            goals_b += 1

    # Add a bit of extra randomness for a more interesting scoreline
    if random.random() < 0.18:
        goals_a += 1
    if random.random() < 0.18:
        goals_b += 1

    if goals_a == goals_b:
        # If tied, a penalty shootout decides the winner
        winner = team_a if random.random() < 0.5 else team_b
        return goals_a, goals_b, winner, True

    winner = team_a if goals_a > goals_b else team_b
    return goals_a, goals_b, winner, False


def simulate_round_of_16(teams_by_name):
    fixtures = [
        ("France", "Paraguay"),
        ("Argentina", "Egypt"),
        ("Spain", "Portugal"),
        ("England", "Mexico"),
        ("Brazil", "Norway"),
        ("Morocco", "Canada"),
        ("Belgium", "United States"),
        ("Switzerland", "Colombia"),
    ]

    round_of_16_winners = []
    for home, away in fixtures:
        team_a = teams_by_name[home]
        team_b = teams_by_name[away]
        goals_a, goals_b, winner, penalty = simulate_match(team_a, team_b)
        round_of_16_winners.append((home, away, winner["Country"], goals_a, goals_b, penalty))
    return round_of_16_winners


def simulate_quarter_finals(round_of_16_winners, teams_by_name):
    quarter_finals = [
        (round_of_16_winners[0][2], round_of_16_winners[1][2]),
        (round_of_16_winners[2][2], round_of_16_winners[3][2]),
        (round_of_16_winners[4][2], round_of_16_winners[5][2]),
        (round_of_16_winners[6][2], round_of_16_winners[7][2]),
    ]

    results = []
    for team_a_name, team_b_name in quarter_finals:
        team_a = teams_by_name[team_a_name]
        team_b = teams_by_name[team_b_name]
        goals_a, goals_b, winner, penalty = simulate_match(team_a, team_b)
        results.append((team_a_name, team_b_name, winner["Country"], goals_a, goals_b, penalty))
    return results


def main():
    teams = load_teams(DATA_FILE)
    teams_by_name = {team["Country"]: team for team in teams}

    round_of_16_winners = simulate_round_of_16(teams_by_name)
    quarter_final_results = simulate_quarter_finals(round_of_16_winners, teams_by_name)

    print("Simulated Round of 16 winners:")
    for home, away, winner, goals_a, goals_b, penalty in round_of_16_winners:
        extra = " (penalties)" if penalty else ""
        print(f"- {home} {goals_a}-{goals_b} {away} -> {winner}{extra}")

    print("\nSimulated Quarter-Final matches:")
    for team_a, team_b, winner, goals_a, goals_b, penalty in quarter_final_results:
        extra = " (penalties)" if penalty else ""
        print(f"- {team_a} {goals_a}-{goals_b} {team_b} -> {winner}{extra}")


if __name__ == "__main__":
    main()
