from datetime import datetime
from flask_login import UserMixin
from extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    favorite_team = db.Column(db.String(100))
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    is_approved = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    predictions = db.relationship("Prediction", backref="user", lazy=True)

    @property
    def total_points(self):
        return sum(p.points_awarded or 0 for p in self.predictions)

    @property
    def exact_scores(self):
        return sum(1 for p in self.predictions if p.points_awarded == 3)

    @property
    def correct_outcomes(self):
        return sum(1 for p in self.predictions if p.points_awarded == 1)


class Match(db.Model):
    __tablename__ = "matches"

    id = db.Column(db.Integer, primary_key=True)
    stage = db.Column(db.String(20), nullable=False)  # group, r32, r16, qf, sf, 3rd, final
    group_label = db.Column(db.String(2), nullable=True)  # A-L, group stage only
    team_home = db.Column(db.String(100), nullable=False)
    team_away = db.Column(db.String(100), nullable=False)
    score_home = db.Column(db.Integer, nullable=True)
    score_away = db.Column(db.Integer, nullable=True)
    match_date = db.Column(db.DateTime, nullable=False)
    is_open = db.Column(db.Boolean, default=False, nullable=False)
    locked_at = db.Column(db.DateTime, nullable=True)

    predictions = db.relationship("Prediction", backref="match", lazy=True)

    @property
    def has_result(self):
        return self.score_home is not None and self.score_away is not None

    @property
    def result_str(self):
        if self.has_result:
            return f"{self.score_home} – {self.score_away}"
        return "— vs —"


class Prediction(db.Model):
    __tablename__ = "predictions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    match_id = db.Column(db.Integer, db.ForeignKey("matches.id"), nullable=False)
    pred_home = db.Column(db.Integer, nullable=False)
    pred_away = db.Column(db.Integer, nullable=False)
    points_awarded = db.Column(db.Integer, nullable=True)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("user_id", "match_id", name="uq_user_match"),
    )
