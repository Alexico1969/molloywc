from datetime import datetime, timedelta
from itertools import combinations


FLAG_EMOJI = {
    "Mexico": "🇲🇽",
    "South Korea": "🇰🇷",
    "South Africa": "🇿🇦",
    "Czechia": "🇨🇿",
    "Canada": "🇨🇦",
    "Switzerland": "🇨🇭",
    "Qatar": "🇶🇦",
    "Bosnia & Herzegovina": "🇧🇦",
    "Brazil": "🇧🇷",
    "Morocco": "🇲🇦",
    "Scotland": "🏴󠁧󠁢󠁳󠁣󠁴󠁿",
    "Haiti": "🇭🇹",
    "USA": "🇺🇸",
    "Paraguay": "🇵🇾",
    "Australia": "🇦🇺",
    "Türkiye": "🇹🇷",
    "Germany": "🇩🇪",
    "Ecuador": "🇪🇨",
    "Côte d'Ivoire": "🇨🇮",
    "Curaçao": "🇨🇼",
    "Netherlands": "🇳🇱",
    "Japan": "🇯🇵",
    "Tunisia": "🇹🇳",
    "Sweden": "🇸🇪",
    "Belgium": "🇧🇪",
    "Iran": "🇮🇷",
    "Egypt": "🇪🇬",
    "New Zealand": "🇳🇿",
    "Spain": "🇪🇸",
    "Uruguay": "🇺🇾",
    "Saudi Arabia": "🇸🇦",
    "Cape Verde": "🇨🇻",
    "France": "🇫🇷",
    "Senegal": "🇸🇳",
    "Norway": "🇳🇴",
    "Iraq": "🇮🇶",
    "Argentina": "🇦🇷",
    "Austria": "🇦🇹",
    "Algeria": "🇩🇿",
    "Jordan": "🇯🇴",
    "Portugal": "🇵🇹",
    "Colombia": "🇨🇴",
    "Uzbekistan": "🇺🇿",
    "DR Congo": "🇨🇩",
    "England": "🏴󠁧󠁢󠁥󠁮󠁧󠁿",
    "Croatia": "🇭🇷",
    "Panama": "🇵🇦",
    "Ghana": "🇬🇭",
    "TBD": "🏳️",
}

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

WC_TEAMS = [t for t in FLAG_EMOJI if t != "TBD"]

STAGE_ORDER = ["group", "r32", "r16", "qf", "sf", "3rd", "final"]
STAGE_LABELS = {
    "group": "Group Stage",
    "r32": "Round of 32",
    "r16": "Round of 16",
    "qf": "Quarter-Finals",
    "sf": "Semi-Finals",
    "3rd": "Third Place",
    "final": "Final",
}


def calculate_points(pred_home, pred_away, score_home, score_away):
    if pred_home == score_home and pred_away == score_away:
        return 3
    if _outcome(pred_home, pred_away) == _outcome(score_home, score_away):
        return 1
    return 0


def _outcome(home, away):
    if home > away:
        return "home"
    if away > home:
        return "away"
    return "draw"


def seed_db(db, bcrypt, User, Match, Prediction):
    if User.query.first():
        return  # already seeded

    admin = User(
        name="Admin",
        email="avanwinkel@molloyhs.org",
        password_hash=bcrypt.generate_password_hash("changeme123").decode("utf-8"),
        favorite_team="USA",
        is_admin=True,
        is_approved=True,
    )
    db.session.add(admin)

    # Group stage: 12 groups × 6 matches = 72 matches
    # Matchday 1: June 12-14, MD2: June 17-20, MD3: June 25-27
    md_bases = [
        datetime(2026, 6, 12, 15, 0),
        datetime(2026, 6, 17, 15, 0),
        datetime(2026, 6, 25, 15, 0),
    ]

    group_list = list(GROUPS.items())
    for g_idx, (label, teams) in enumerate(group_list):
        matchups = list(combinations(teams, 2))  # 6 match pairings
        # 2 games per matchday
        for m_idx, (home, away) in enumerate(matchups):
            md = m_idx // 2  # 0, 0, 1, 1, 2, 2
            slot = m_idx % 2  # morning / afternoon slot
            day_shift = g_idx % 3  # spread groups across days within window
            match_date = md_bases[md] + timedelta(days=day_shift, hours=slot * 3)
            db.session.add(Match(
                stage="group",
                group_label=label,
                team_home=home,
                team_away=away,
                match_date=match_date,
                is_open=False,
            ))

    # Knockout placeholder matches
    knockout_stages = [
        ("r32", 16, datetime(2026, 6, 29, 15, 0)),
        ("r16", 8,  datetime(2026, 7, 4, 15, 0)),
        ("qf",  4,  datetime(2026, 7, 9, 15, 0)),
        ("sf",  2,  datetime(2026, 7, 14, 15, 0)),
        ("3rd", 1,  datetime(2026, 7, 18, 15, 0)),
        ("final", 1, datetime(2026, 7, 19, 19, 0)),
    ]
    for stage, count, start_date in knockout_stages:
        for i in range(count):
            db.session.add(Match(
                stage=stage,
                group_label=None,
                team_home="TBD",
                team_away="TBD",
                match_date=start_date + timedelta(days=i // 2, hours=(i % 2) * 3),
                is_open=False,
            ))

    db.session.commit()
    print("=" * 50)
    print("Database seeded.")
    print("Admin: avanwinkel@molloyhs.org / changeme123")
    print("IMPORTANT: Change admin password after first login!")
    print("=" * 50)
