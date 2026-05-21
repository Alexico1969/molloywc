from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, make_response
from flask_login import login_required, current_user
from extensions import db
from models import User, Match, Prediction
from utils import calculate_points, STAGE_ORDER, STAGE_LABELS

user_bp = Blueprint("user", __name__)


def _require_approved():
    if not current_user.is_approved:
        flash("Your account has been disabled.", "danger")
        return redirect(url_for("auth.logout"))
    return None


@user_bp.route("/")
def index():
    from models import User, Match
    leaderboard = (
        User.query.filter_by(is_approved=True)
        .all()
    )
    leaderboard = sorted(leaderboard, key=lambda u: u.total_points, reverse=True)[:5]
    return render_template("index.html", leaderboard=leaderboard)


@user_bp.route("/dashboard")
@login_required
def dashboard():
    redir = _require_approved()
    if redir:
        return redir

    predicted_ids = {p.match_id for p in current_user.predictions}
    open_matches = (
        Match.query
        .filter_by(is_open=True)
        .filter(Match.id.notin_(predicted_ids) if predicted_ids else Match.id.isnot(None))
        .order_by(Match.match_date)
        .limit(10)
        .all()
    )

    all_users = sorted(
        User.query.filter_by(is_approved=True).all(),
        key=lambda u: u.total_points,
        reverse=True,
    )
    rank = next((i + 1 for i, u in enumerate(all_users) if u.id == current_user.id), None)

    return render_template(
        "user/dashboard.html",
        open_matches=open_matches,
        rank=rank,
        total_users=len(all_users),
    )


@user_bp.route("/predict")
@login_required
def predict():
    redir = _require_approved()
    if redir:
        return redir

    predicted_ids = {p.match_id for p in current_user.predictions}
    open_matches = (
        Match.query
        .filter_by(is_open=True)
        .filter(~Match.id.in_(predicted_ids) if predicted_ids else Match.id.isnot(None))
        .order_by(Match.match_date)
        .all()
    )

    by_stage = {}
    for stage in STAGE_ORDER:
        matches = [m for m in open_matches if m.stage == stage]
        if matches:
            by_stage[stage] = matches

    return render_template("user/predict.html", by_stage=by_stage, stage_labels=STAGE_LABELS)


@user_bp.route("/predict/<int:match_id>", methods=["POST"])
@login_required
def submit_prediction(match_id):
    redir = _require_approved()
    if redir:
        return redir

    match = Match.query.get_or_404(match_id)

    if not match.is_open or match.has_result:
        flash("Predictions are not accepted for this match.", "danger")
        return redirect(url_for("user.predict"))

    try:
        pred_home = int(request.form["pred_home"])
        pred_away = int(request.form["pred_away"])
    except (KeyError, ValueError):
        flash("Invalid score entered.", "danger")
        return redirect(url_for("user.predict"))

    if pred_home < 0 or pred_away < 0:
        flash("Scores cannot be negative.", "danger")
        return redirect(url_for("user.predict"))

    existing = Prediction.query.filter_by(
        user_id=current_user.id, match_id=match_id
    ).first()

    if existing:
        existing.pred_home = pred_home
        existing.pred_away = pred_away
        flash("Prediction updated!", "success")
    else:
        db.session.add(Prediction(
            user_id=current_user.id,
            match_id=match_id,
            pred_home=pred_home,
            pred_away=pred_away,
        ))
        flash("Prediction submitted!", "success")

    db.session.commit()
    return redirect(url_for("user.predict"))


@user_bp.route("/my-predictions")
@login_required
def my_predictions():
    redir = _require_approved()
    if redir:
        return redir

    preds = (
        Prediction.query
        .filter_by(user_id=current_user.id)
        .join(Match)
        .order_by(Match.match_date)
        .all()
    )

    by_stage = {}
    for stage in STAGE_ORDER:
        stage_preds = [p for p in preds if p.match.stage == stage]
        if stage_preds:
            subtotal = sum(p.points_awarded or 0 for p in stage_preds)
            by_stage[stage] = {"preds": stage_preds, "subtotal": subtotal}

    return render_template(
        "user/my_predictions.html",
        by_stage=by_stage,
        stage_labels=STAGE_LABELS,
    )


@user_bp.route("/leaderboard")
@login_required
def leaderboard():
    redir = _require_approved()
    if redir:
        return redir

    users = sorted(
        User.query.filter_by(is_approved=True).all(),
        key=lambda u: (u.total_points, u.exact_scores),
        reverse=True,
    )
    return render_template("user/leaderboard.html", users=users)


@user_bp.route("/my-predictions/export-pdf")
@login_required
def export_predictions_pdf():
    redir = _require_approved()
    if redir:
        return redir

    from io import BytesIO
    from datetime import datetime as dt
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

    NAVY = colors.HexColor("#002366")
    GOLD = colors.HexColor("#C9A84C")
    LIGHT_ROW = colors.HexColor("#f4f6fb")

    preds = (
        Prediction.query
        .filter_by(user_id=current_user.id)
        .join(Match)
        .order_by(Match.match_date)
        .all()
    )

    by_stage = {}
    for stage in STAGE_ORDER:
        stage_preds = [p for p in preds if p.match.stage == stage]
        if stage_preds:
            subtotal = sum(p.points_awarded or 0 for p in stage_preds)
            by_stage[stage] = {"preds": stage_preds, "subtotal": subtotal}

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.5 * inch,
        leftMargin=0.5 * inch,
        topMargin=0.5 * inch,
        bottomMargin=0.5 * inch,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "PredTitle",
        parent=styles["Heading1"],
        textColor=NAVY,
        fontSize=18,
        spaceAfter=2,
    )
    subtitle_style = ParagraphStyle(
        "PredSubtitle",
        parent=styles["Normal"],
        textColor=colors.HexColor("#6c757d"),
        fontSize=10,
        spaceAfter=14,
    )
    stage_style = ParagraphStyle(
        "StageHeader",
        parent=styles["Normal"],
        textColor=colors.white,
        backColor=NAVY,
        fontSize=10,
        fontName="Helvetica-Bold",
        spaceBefore=10,
        spaceAfter=2,
        leftIndent=0,
        leading=18,
    )

    story = []
    story.append(Paragraph(f"My Predictions — {current_user.name}", title_style))
    story.append(Paragraph(
        f"Total: {current_user.total_points} pts  |  "
        f"{current_user.exact_scores} exact  |  "
        f"{current_user.correct_outcomes} correct result  |  "
        f"Generated {dt.utcnow().strftime('%b %d, %Y')}",
        subtitle_style,
    ))

    col_widths = [0.65 * inch, 3.3 * inch, 0.9 * inch, 0.9 * inch, 0.6 * inch]

    for stage, data in by_stage.items():
        label = STAGE_LABELS.get(stage, stage)
        story.append(Paragraph(f"  {label}  —  Subtotal: {data['subtotal']} pts", stage_style))

        rows = [["Date", "Match", "Your Pick", "Result", "Points"]]
        for p in data["preds"]:
            date_str = p.match.match_date.strftime("%b %d")
            match_str = f"{p.match.team_home} vs {p.match.team_away}"
            pick_str = f"{p.pred_home} – {p.pred_away}"
            result_str = (
                f"{p.match.score_home} – {p.match.score_away}"
                if p.match.has_result else "Pending"
            )
            if p.points_awarded is None:
                pts_str = "—"
            elif p.points_awarded == 3:
                pts_str = "+3"
            elif p.points_awarded == 1:
                pts_str = "+1"
            else:
                pts_str = "0"
            rows.append([date_str, match_str, pick_str, result_str, pts_str])

        table = Table(rows, colWidths=col_widths, repeatRows=1)
        ts = TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (2, 0), (-1, -1), "CENTER"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT_ROW]),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#dee2e6")),
            ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ])
        for i, p in enumerate(data["preds"], start=1):
            if p.points_awarded == 3:
                ts.add("TEXTCOLOR", (4, i), (4, i), colors.HexColor("#198754"))
                ts.add("FONTNAME", (4, i), (4, i), "Helvetica-Bold")
            elif p.points_awarded == 1:
                ts.add("TEXTCOLOR", (4, i), (4, i), colors.HexColor("#0d6efd"))
                ts.add("FONTNAME", (4, i), (4, i), "Helvetica-Bold")
        table.setStyle(ts)
        story.append(table)

    doc.build(story)
    buffer.seek(0)

    safe_name = current_user.name.replace(" ", "_")
    filename = f"predictions_{safe_name}.pdf"
    response = make_response(buffer.read())
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response


@user_bp.route("/schedule")
@login_required
def schedule():
    redir = _require_approved()
    if redir:
        return redir

    matches = Match.query.order_by(Match.match_date).all()
    predicted = {p.match_id: p for p in current_user.predictions}

    by_stage = {}
    for stage in STAGE_ORDER:
        stage_matches = [m for m in matches if m.stage == stage]
        if stage_matches:
            by_stage[stage] = stage_matches

    return render_template(
        "user/schedule.html",
        by_stage=by_stage,
        stage_labels=STAGE_LABELS,
        predicted=predicted,
    )
