from datetime import datetime
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from extensions import db
from models import User, Match, Prediction
from utils import calculate_points, STAGE_ORDER, STAGE_LABELS

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def require_admin():
    if not current_user.is_authenticated or not current_user.is_admin:
        abort(403)


@admin_bp.route("/")
@login_required
def dashboard():
    require_admin()
    stats = {
        "users": User.query.count(),
        "matches": Match.query.count(),
        "predictions": Prediction.query.count(),
        "open_matches": Match.query.filter_by(is_open=True).count(),
        "pending_results": Match.query.filter(
            Match.is_open == False,
            Match.score_home == None,
            Match.locked_at == None,
            Match.stage == "group",
        ).count(),
    }
    return render_template("admin/dashboard.html", stats=stats)


@admin_bp.route("/users")
@login_required
def users():
    require_admin()
    all_users = User.query.order_by(User.created_at).all()
    return render_template("admin/users.html", users=all_users)


@admin_bp.route("/users/<int:user_id>/toggle-approved", methods=["POST"])
@login_required
def toggle_approved(user_id):
    require_admin()
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot disable your own account.", "danger")
        return redirect(url_for("admin.users"))
    user.is_approved = not user.is_approved
    db.session.commit()
    status = "enabled" if user.is_approved else "disabled"
    flash(f"Account {status} for {user.name}.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/toggle-admin", methods=["POST"])
@login_required
def toggle_admin(user_id):
    require_admin()
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot change your own admin status.", "danger")
        return redirect(url_for("admin.users"))
    user.is_admin = not user.is_admin
    db.session.commit()
    status = "promoted to admin" if user.is_admin else "demoted from admin"
    flash(f"{user.name} {status}.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/users/<int:user_id>/delete", methods=["POST"])
@login_required
def delete_user(user_id):
    require_admin()
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("You cannot delete your own account.", "danger")
        return redirect(url_for("admin.users"))
    Prediction.query.filter_by(user_id=user.id).delete()
    db.session.delete(user)
    db.session.commit()
    flash(f"User {user.name} deleted.", "success")
    return redirect(url_for("admin.users"))


@admin_bp.route("/matches")
@login_required
def matches():
    require_admin()
    all_matches = Match.query.order_by(Match.match_date).all()
    by_stage = {}
    for stage in STAGE_ORDER:
        stage_matches = [m for m in all_matches if m.stage == stage]
        if stage_matches:
            by_stage[stage] = stage_matches
    return render_template("admin/matches.html", by_stage=by_stage, stage_labels=STAGE_LABELS)


@admin_bp.route("/matches/<int:match_id>/set-result", methods=["POST"])
@login_required
def set_result(match_id):
    require_admin()
    match = Match.query.get_or_404(match_id)

    try:
        score_home = int(request.form["score_home"])
        score_away = int(request.form["score_away"])
    except (KeyError, ValueError):
        flash("Invalid scores.", "danger")
        return redirect(url_for("admin.matches"))

    if score_home < 0 or score_away < 0:
        flash("Scores cannot be negative.", "danger")
        return redirect(url_for("admin.matches"))

    match.score_home = score_home
    match.score_away = score_away
    match.is_open = False
    match.locked_at = datetime.utcnow()

    for pred in match.predictions:
        pred.points_awarded = calculate_points(
            pred.pred_home, pred.pred_away, score_home, score_away
        )

    db.session.commit()
    flash(
        f"Result set: {match.team_home} {score_home} – {score_away} {match.team_away}. "
        f"Points calculated for {len(match.predictions)} prediction(s).",
        "success",
    )
    return redirect(url_for("admin.matches"))


@admin_bp.route("/matches/<int:match_id>/toggle-open", methods=["POST"])
@login_required
def toggle_open(match_id):
    require_admin()
    match = Match.query.get_or_404(match_id)
    if match.has_result:
        flash("Cannot reopen a match that already has a result.", "warning")
        return redirect(url_for("admin.matches"))
    match.is_open = not match.is_open
    db.session.commit()
    status = "opened" if match.is_open else "closed"
    flash(f"Match {status} for predictions.", "success")
    return redirect(url_for("admin.matches"))


@admin_bp.route("/matches/<int:match_id>/update-date", methods=["POST"])
@login_required
def update_date(match_id):
    require_admin()
    match = Match.query.get_or_404(match_id)
    raw = request.form.get("match_date", "").strip()
    try:
        match.match_date = datetime.strptime(raw, "%Y-%m-%dT%H:%M")
    except ValueError:
        flash("Invalid date format.", "danger")
        return redirect(url_for("admin.matches"))
    db.session.commit()
    flash(f"Date updated for {match.team_home} vs {match.team_away}.", "success")
    return redirect(url_for("admin.matches"))


@admin_bp.route("/matches/<int:match_id>/update-teams", methods=["POST"])
@login_required
def update_teams(match_id):
    require_admin()
    match = Match.query.get_or_404(match_id)
    team_home = request.form.get("team_home", "").strip()
    team_away = request.form.get("team_away", "").strip()
    if team_home:
        match.team_home = team_home
    if team_away:
        match.team_away = team_away
    db.session.commit()
    flash("Match teams updated.", "success")
    return redirect(url_for("admin.matches"))


@admin_bp.route("/matches/open-stage")
@login_required
def open_stage():
    require_admin()
    stage = request.args.get("stage", "group")
    matches = Match.query.filter_by(stage=stage).filter(Match.score_home == None).all()
    count = 0
    for m in matches:
        if not m.is_open:
            m.is_open = True
            count += 1
    db.session.commit()
    label = STAGE_LABELS.get(stage, stage)
    flash(f"Opened {count} {label} match(es) for predictions.", "success")
    return redirect(url_for("admin.matches"))


@admin_bp.route("/predictions")
@login_required
def predictions():
    require_admin()
    all_users = User.query.order_by(User.name).all()
    all_matches = Match.query.order_by(Match.match_date).all()

    selected_user_id = request.args.get("user_id", type=int)
    selected_match_id = request.args.get("match_id", type=int)

    query = Prediction.query.join(Match).join(User)
    if selected_user_id:
        query = query.filter(Prediction.user_id == selected_user_id)
    if selected_match_id:
        query = query.filter(Prediction.match_id == selected_match_id)

    preds = query.order_by(Match.match_date, User.name).all()

    return render_template(
        "admin/predictions.html",
        preds=preds,
        all_users=all_users,
        all_matches=all_matches,
        selected_user_id=selected_user_id,
        selected_match_id=selected_match_id,
    )
