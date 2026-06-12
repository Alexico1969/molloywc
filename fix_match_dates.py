"""
Run once to correct group-stage match dates in the existing database.
The original seed used itertools.combinations which placed team[0] twice
on Matchday 1 and team[3] twice on Matchday 3 for every group.
"""
from datetime import datetime, timedelta

GROUPS = {
    "A": ["Mexico", "South Korea", "South Africa", "Czechia"],
    "B": ["Canada", "Switzerland", "Qatar", "Bosnia & Herzegovina"],
    "C": ["Brazil", "Morocco", "Scotland", "Haiti"],
    "D": ["USA", "Paraguay", "Australia", "Türkiye"],
    "E": ["Germany", "Ecuador", "Côte d'Ivoire", "Curaçao"],
    "F": ["Netherlands", "Japan", "Tunisia", "Sweden"],
    "G": ["Belgium", "Iran", "Egypt", "New Zealand"],
    "H": ["Spain", "Uruguay", "Saudi Arabia", "Cape Verde"],
    "I": ["France", "Senegal", "Norway", "Iraq"],
    "J": ["Argentina", "Austria", "Algeria", "Jordan"],
    "K": ["Portugal", "Colombia", "Uzbekistan", "DR Congo"],
    "L": ["England", "Croatia", "Panama", "Ghana"],
}

MD_BASES = [
    datetime(2026, 6, 12, 15, 0),
    datetime(2026, 6, 17, 15, 0),
    datetime(2026, 6, 25, 15, 0),
]


def correct_matchups(teams):
    return [
        (teams[0], teams[1]), (teams[2], teams[3]),
        (teams[0], teams[2]), (teams[1], teams[3]),
        (teams[0], teams[3]), (teams[1], teams[2]),
    ]


def fix(app, db, Match):
    with app.app_context():
        updated = 0
        group_list = list(GROUPS.items())
        for g_idx, (label, teams) in enumerate(group_list):
            day_shift = g_idx % 3
            matchups = correct_matchups(teams)
            for m_idx, (home, away) in enumerate(matchups):
                md = m_idx // 2
                slot = m_idx % 2
                correct_date = MD_BASES[md] + timedelta(days=day_shift, hours=slot * 3)

                match = Match.query.filter_by(
                    stage="group", group_label=label,
                    team_home=home, team_away=away,
                ).first()

                if match is None:
                    print(f"  NOT FOUND: Group {label} {home} vs {away}")
                    continue

                if match.match_date != correct_date:
                    print(f"  Group {label}: {home} vs {away}  "
                          f"{match.match_date.strftime('%b %d %H:%M')} -> "
                          f"{correct_date.strftime('%b %d %H:%M')}")
                    match.match_date = correct_date
                    updated += 1

        db.session.commit()
        print(f"\nDone — {updated} match dates corrected.")


if __name__ == "__main__":
    from flask_app import app, db
    from models import Match
    fix(app, db, Match)
