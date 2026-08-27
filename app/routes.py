from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User, DSAProblem, SQLPractice, Company, MockInterview
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from collections import defaultdict
import calendar

auth = Blueprint("auth", __name__)
main = Blueprint("main", __name__)


# ===== AUTH ROUTES =====

@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        college = request.form.get("college")

        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("Email already registered.", "danger")
            return redirect(url_for("auth.register"))

        hashed_password = generate_password_hash(password)
        new_user = User(name=name, email=email,
                        password=hashed_password, college=college)
        db.session.add(new_user)
        db.session.commit()
        flash("Account created! Please log in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("auth.login"))

        login_user(user)
        return redirect(url_for("main.dashboard"))

    return render_template("login.html")


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))


# ===== MAIN ROUTES =====

# -----------------------------------------
# Helper Function
# -----------------------------------------
def calculate_streak(user_id):
    """
    Returns:
        current_streak
        longest_streak

    Rules:
    - Multiple activities on the same day count as ONE day.
    - Missing yesterday resets current streak to 0.
    - Longest streak is preserved.
    """

    activity_days = set()

    # ---------------- DSA ----------------

    dsa_dates = db.session.query(
        DSAProblem.date_solved
    ).filter_by(
        user_id=user_id
    ).all()

    for d in dsa_dates:
        if d[0]:
            activity_days.add(d[0])

    # ---------------- SQL ----------------

    sql_dates = db.session.query(
        SQLPractice.practice_date
    ).filter_by(
        user_id=user_id
    ).all()

    for d in sql_dates:
        if d[0]:
            activity_days.add(d[0])

    # ---------------- Mock ----------------

    mock_dates = db.session.query(
        MockInterview.mock_date
    ).filter_by(
        user_id=user_id
    ).all()

    for d in mock_dates:
        if d[0]:
            activity_days.add(d[0])

    # -------------------------------------

    if not activity_days:
        return 0, 0

    days = sorted(activity_days)

    # ========= Longest Streak =========

    longest = 1
    streak = 1

    for i in range(1, len(days)):

        if days[i] == days[i - 1] + timedelta(days=1):

            streak += 1

        else:

            longest = max(longest, streak)

            streak = 1

    longest = max(longest, streak)

    # ========= Current Streak =========

    today = datetime.today().date()

    if today in activity_days:

        current = 1
        check_day = today

    elif (today - timedelta(days=1)) in activity_days:

        current = 1
        check_day = today - timedelta(days=1)

    else:

        return 0, longest

    while True:

        previous = check_day - timedelta(days=1)

        if previous in activity_days:

            current += 1
            check_day = previous

        else:

            break

    return current, longest


def build_recent_activity(user_id):

    activities = []

    # ---------- Latest DSA ----------
    dsa = (
        DSAProblem.query
        .filter_by(user_id=user_id)
        .order_by(DSAProblem.date_solved.desc())
        .limit(5)
        .all()
    )

    for problem in dsa:

        activities.append({

            "icon": "💻",

            "title": f"Solved {problem.problem_name}",

            "date": problem.date_solved

        })


    # ---------- Latest SQL ----------
    sql = (
        SQLPractice.query
        .filter_by(user_id=user_id)
        .order_by(SQLPractice.practice_date.desc())
        .limit(5)
        .all()
    )

    for topic in sql:

        activities.append({

            "icon": "🗄️",

            "title": f"Completed SQL: {topic.topic}",

            "date": topic.practice_date

        })


    # ---------- Latest Mock ----------
    mock = (
        MockInterview.query
        .filter_by(user_id=user_id)
        .order_by(MockInterview.mock_date.desc())
        .limit(5)
        .all()
    )

    for interview in mock:

        activities.append({

            "icon": "🎤",

            "title": f"Mock Interview - Score {interview.score}",

            "date": interview.mock_date

        })


    # ---------- Companies ----------
    # Company has no created_at column,
    # so we use id (latest inserted first)

    company = (
        Company.query
        .filter_by(user_id=user_id)
        .order_by(Company.id.desc())
        .limit(5)
        .all()
    )

    for c in company:

        activities.append({

            "icon": "🏢",

            "title": f"Added {c.company_name}",

            "date": None

        })


    # ---------- Sort ----------

    activities.sort(

        key=lambda x: (

            x["date"] is None,

            -(x["date"].toordinal()) if x["date"] else 0

        )

    )

    return activities[:5]

def calculate_today_goals(user_id):

    today = datetime.today().date()

    dsa_today = DSAProblem.query.filter_by(
        user_id=user_id,
        date_solved=today
    ).count()

    sql_today = SQLPractice.query.filter_by(
        user_id=user_id,
        practice_date=today
    ).count()

    mock_today = MockInterview.query.filter_by(
        user_id=user_id,
        mock_date=today
    ).count()

    # Company model has no date column
    company_today = 0

    goals = {

        "dsa": min(dsa_today, 2),

        "sql": min(sql_today, 1),

        "mock": min(mock_today, 1),

        "company": company_today

    }

    completed = 0

    if goals["dsa"] >= 2:
        completed += 1

    if goals["sql"] >= 1:
        completed += 1

    if goals["mock"] >= 1:
        completed += 1

    if goals["company"] >= 1:
        completed += 1

    progress = round((completed / 4) * 100)

    return goals, progress

def calculate_next_targets(user_id):

    # ---------- DSA ----------
    total_dsa = DSAProblem.query.filter_by(user_id=user_id).count()
    dsa_milestones = [10, 25, 50, 100, 200]

    next_dsa = next((m for m in dsa_milestones if total_dsa < m), dsa_milestones[-1])

    # ---------- SQL ----------
    completed_sql = SQLPractice.query.filter_by(
        user_id=user_id,
        status="Completed"
    ).count()

    sql_milestones = [1, 5, 10, 20]

    next_sql = next((m for m in sql_milestones if completed_sql < m), sql_milestones[-1])

    # ---------- Company ----------
    total_company = Company.query.filter_by(user_id=user_id).count()

    company_milestones = [3, 5, 10, 20]

    next_company = next((m for m in company_milestones if total_company < m), company_milestones[-1])

    # ---------- Mock ----------
    mocks = MockInterview.query.filter_by(user_id=user_id).all()

    if mocks:
        avg = round(sum(m.score for m in mocks) / len(mocks))
    else:
        avg = 0

    if avg < 70:
        next_mock = 70
    elif avg < 85:
        next_mock = 85
    else:
        next_mock = 100

    return {

        "dsa_remaining": next_dsa - total_dsa,
        "dsa_target": next_dsa,

        "sql_remaining": next_sql - completed_sql,
        "sql_target": next_sql,

        "company_remaining": next_company - total_company,
        "company_target": next_company,

        "current_mock": avg,
        "mock_target": next_mock

    }

from datetime import date, timedelta
from collections import defaultdict
import calendar

from flask import render_template
from flask_login import login_required, current_user

# adjust to your actual model import paths
# from .models import DSAProblem, SQLPractice, MockInterview


def build_practice_heatmap(user_id):
    today = date.today()
    start_date = today - timedelta(days=364)
    start_date -= timedelta(days=start_date.weekday())  # snap to Monday

    activity = defaultdict(lambda: {"dsa": 0, "sql": 0, "mock": 0})

    for record in DSAProblem.query.filter_by(user_id=user_id).all():
        if record.date_solved:
            activity[record.date_solved]["dsa"] += 1

    for record in SQLPractice.query.filter_by(user_id=user_id).all():
        if record.practice_date:
            activity[record.practice_date]["sql"] += 1

    for record in MockInterview.query.filter_by(user_id=user_id).all():
        if record.mock_date:
            activity[record.mock_date]["mock"] += 1

    total_activities = 0
    active_days = 0
    max_activity = 0

    for value in activity.values():
        total = value["dsa"] + value["sql"] + value["mock"]
        total_activities += total
        if total > 0:
            active_days += 1
        max_activity = max(max_activity, total)

    if max_activity == 0:
        max_activity = 1

    weeks = []
    current = start_date

    while current <= today:
        week = []
        for i in range(7):
            day = current + timedelta(days=i)
            value = activity[day]
            total = value["dsa"] + value["sql"] + value["mock"]

            if total == 0:
                level = 0
            else:
                pct = total / max_activity
                level = 1 if pct <= 0.25 else 2 if pct <= 0.50 else 3 if pct <= 0.75 else 4

            week.append({
                "date": day.strftime("%Y-%m-%d"),
                "day": calendar.day_abbr[day.weekday()],
                "month": day.strftime("%b"),
                "day_number": day.day,
                "year": day.year,
                "dsa": value["dsa"],
                "sql": value["sql"],
                "mock": value["mock"],
                "total": total,
                "level": level,
                "future": day > today,
            })
        weeks.append(week)
        current += timedelta(days=7)

    months = []
    previous_month = None
    for index, week in enumerate(weeks):
        month = week[0]["month"]
        if month != previous_month:
            months.append({"label": month, "column": index})
            previous_month = month

    stats = {
        "total_activities": total_activities,
        "active_days": active_days,
        "max_activity": max_activity,
        "weeks": len(weeks),
    }

    return {"weeks": weeks, "months": months, "stats": stats}




# -----------------------------------------
# Dashboard Route
# -----------------------------------------


@main.route("/")
@login_required
def dashboard():

    # ---------- Dashboard Cards ----------
    total_dsa = DSAProblem.query.filter_by(
        user_id=current_user.id
    ).count()

    completed_sql = SQLPractice.query.filter_by(
        user_id=current_user.id,
        status="Completed"
    ).count()

    total_companies = Company.query.filter_by(
        user_id=current_user.id
    ).count()

    mock_interviews = MockInterview.query.filter_by(
        user_id=current_user.id
    ).order_by(MockInterview.mock_date).all()

    total_mock = len(mock_interviews)

    mock_scores = [m.score for m in mock_interviews]

    avg_score = round(
        sum(mock_scores) / len(mock_scores), 1
    ) if mock_scores else 0

    # ---------- Preparation Score ----------
    preparation_score = round(
        (
            (min(total_dsa, 50) / 50) * 30 +
            (min(completed_sql, 20) / 20) * 20 +
            (min(total_companies, 10) / 10) * 20 +
            (avg_score / 100) * 30
        ),
        1
    )

    # ---------- DSA Analytics ----------
    easy = DSAProblem.query.filter_by(
        user_id=current_user.id,
        difficulty="Easy"
    ).count()

    medium = DSAProblem.query.filter_by(
        user_id=current_user.id,
        difficulty="Medium"
    ).count()

    hard = DSAProblem.query.filter_by(
        user_id=current_user.id,
        difficulty="Hard"
    ).count()

    # ---------- SQL Analytics ----------
    progress = SQLPractice.query.filter_by(
        user_id=current_user.id,
        status="In Progress"
    ).count()

    pending = SQLPractice.query.filter_by(
        user_id=current_user.id,
        status="Not Started"
    ).count()

    # ---------- Company Analytics ----------
    planning = Company.query.filter_by(
        user_id=current_user.id,
        status="Planning"
    ).count()

    preparing = Company.query.filter_by(
        user_id=current_user.id,
        status="Preparing"
    ).count()

    applied = Company.query.filter_by(
        user_id=current_user.id,
        status="Applied"
    ).count()

    interview = Company.query.filter_by(
        user_id=current_user.id,
        status="Interview"
    ).count()

    offer = Company.query.filter_by(
        user_id=current_user.id,
        status="Offer"
    ).count()

   # ==========================
   # Recent Activity
   # ==========================

    activities = build_recent_activity(current_user.id)
    current_streak, longest_streak = calculate_streak(current_user.id)
    today_goals, today_progress = calculate_today_goals(current_user.id)
    next_targets = calculate_next_targets(current_user.id)
    heatmap = build_practice_heatmap(current_user.id)
    
    return render_template(
     "dashboard.html",

    # KPI Cards
    total_dsa=total_dsa,
    completed_sql=completed_sql,
    total_companies=total_companies,
    total_mock=total_mock,
    avg_score=avg_score,
    preparation_score=preparation_score,

    # DSA Analytics
    easy=easy,
    medium=medium,
    hard=hard,

    # SQL Analytics
    completed=completed_sql,
    progress=progress,
    pending=pending,

    # Company Analytics
    planning=planning,
    preparing=preparing,
    applied=applied,
    interview=interview,
    offer=offer,

    # Mock Analytics
    mock_data=mock_interviews,

    activities=activities,

    current_streak=current_streak,
    longest_streak=longest_streak,
    today_goals=today_goals,
    today_progress=today_progress,
    next_targets=next_targets,
    heatmap=heatmap,
    
)


@main.route("/dsa")
@login_required
def dsa():
    problems = DSAProblem.query.filter_by(
        user_id=current_user.id).order_by(DSAProblem.id).all()
    return render_template("dsa.html", problems=problems)


@main.route("/dsa/add", methods=["POST"])
@login_required
def add_dsa():
    problem_name = request.form.get("problem_name")
    difficulty = request.form.get("difficulty")
    topic = request.form.get("topic")
    platform = request.form.get("platform")
    date_solved = request.form.get("date_solved")

    new_problem = DSAProblem(
        user_id=current_user.id,
        problem_name=problem_name,
        difficulty=difficulty,
        topic=topic,
        platform=platform,
        date_solved=datetime.strptime(date_solved, "%Y-%m-%d").date()
    )
    db.session.add(new_problem)
    db.session.commit()
    flash("Problem added successfully!", "success")
    return redirect(url_for("main.dsa"))


@main.route("/dsa/delete/<int:id>")
@login_required
def delete_dsa(id):
    problem = DSAProblem.query.get_or_404(id)
    if problem.user_id != current_user.id:
        flash("Unauthorized action.", "danger")
        return redirect(url_for("main.dsa"))
    db.session.delete(problem)
    db.session.commit()
    flash("Problem deleted.", "success")
    return redirect(url_for("main.dsa"))


@main.route("/sql")
@login_required
def sql():
    topics = SQLPractice.query.filter_by(
        user_id=current_user.id).order_by(SQLPractice.id).all()
    return render_template("sql.html", topics=topics)


@main.route("/sql/add", methods=["POST"])
@login_required
def add_sql():
    topic = request.form.get("topic")
    difficulty = request.form.get("difficulty")
    practice_date = request.form.get("practice_date")
    status = request.form.get("status")

    new_topic = SQLPractice(
        user_id=current_user.id,
        topic=topic,
        difficulty=difficulty,
        practice_date=datetime.strptime(practice_date, "%Y-%m-%d").date(),
        status=status
    )
    db.session.add(new_topic)
    db.session.commit()
    flash("SQL topic added successfully!", "success")
    return redirect(url_for("main.sql"))


@main.route("/sql/update/<int:id>", methods=["POST"])
@login_required
def update_sql(id):
    topic = SQLPractice.query.get_or_404(id)
    if topic.user_id != current_user.id:
        flash("Unauthorized action.", "danger")
        return redirect(url_for("main.sql"))
    topic.status = request.form.get("status")
    db.session.commit()
    flash("Status updated successfully!", "success")
    return redirect(url_for("main.sql"))


@main.route("/sql/delete/<int:id>")
@login_required
def delete_sql(id):
    topic = SQLPractice.query.get_or_404(id)
    if topic.user_id != current_user.id:
        flash("Unauthorized action.", "danger")
        return redirect(url_for("main.sql"))
    db.session.delete(topic)
    db.session.commit()
    flash("Topic deleted.", "success")
    return redirect(url_for("main.sql"))


@main.route("/company")
@login_required
def company():
    companies = Company.query.filter_by(
        user_id=current_user.id
    ).order_by(Company.id).all()
    return render_template("company.html", companies=companies)


@main.route("/company/add", methods=["POST"])
@login_required
def add_company():
    company_name = request.form.get("company_name")
    status = request.form.get("status")
    notes = request.form.get("notes")

    new_company = Company(
        user_id=current_user.id,
        company_name=company_name,
        status=status,
        notes=notes
    )

    db.session.add(new_company)
    db.session.commit()
    flash("Company added successfully!", "success")
    return redirect(url_for("main.company"))


@main.route("/company/update/<int:id>", methods=["POST"])
@login_required
def update_company(id):
    company = Company.query.get_or_404(id)

    if company.user_id != current_user.id:
        flash("Unauthorized action.", "danger")
        return redirect(url_for("main.company"))

    company.status = request.form.get("status")
    db.session.commit()
    flash("Company status updated successfully!", "success")
    return redirect(url_for("main.company"))


@main.route("/company/delete/<int:id>")
@login_required
def delete_company(id):
    company = Company.query.get_or_404(id)

    if company.user_id != current_user.id:
        flash("Unauthorized action.", "danger")
        return redirect(url_for("main.company"))

    db.session.delete(company)
    db.session.commit()
    flash("Company deleted successfully!", "success")
    return redirect(url_for("main.company"))


@main.route("/mock")
@login_required
def mock():
    interviews = MockInterview.query.filter_by(
        user_id=current_user.id
    ).order_by(MockInterview.mock_date.desc()).all()

    return render_template(
        "mock.html",
        interviews=interviews
    )


@main.route("/mock/add", methods=["POST"])
@login_required
def add_mock():
    mock_date = request.form.get("mock_date")
    score = request.form.get("score")
    feedback = request.form.get("feedback")

    interview = MockInterview(
        user_id=current_user.id,
        mock_date=datetime.strptime(mock_date, "%Y-%m-%d").date(),
        score=score,
        feedback=feedback
    )

    db.session.add(interview)
    db.session.commit()

    flash("Mock interview added successfully!", "success")

    return redirect(url_for("main.mock"))


@main.route("/mock/delete/<int:id>")
@login_required
def delete_mock(id):
    interview = MockInterview.query.get_or_404(id)

    if interview.user_id != current_user.id:
        flash("Unauthorized action.", "danger")
        return redirect(url_for("main.mock"))

    db.session.delete(interview)
    db.session.commit()

    flash("Mock interview deleted successfully!", "success")

    return redirect(url_for("main.mock"))


@main.route("/analytics")
@login_required
def analytics():

    # ---------- DSA ----------
    easy = DSAProblem.query.filter_by(user_id=current_user.id, difficulty="Easy").count()
    medium = DSAProblem.query.filter_by(user_id=current_user.id, difficulty="Medium").count()
    hard = DSAProblem.query.filter_by(user_id=current_user.id, difficulty="Hard").count()

    # ---------- SQL ----------
    completed = SQLPractice.query.filter_by(user_id=current_user.id, status="Completed").count()
    progress = SQLPractice.query.filter_by(user_id=current_user.id, status="In Progress").count()
    pending = SQLPractice.query.filter_by(user_id=current_user.id, status="Not Started").count()

    # ---------- Company ----------
    planning = Company.query.filter_by(user_id=current_user.id, status="Planning").count()
    preparing = Company.query.filter_by(user_id=current_user.id, status="Preparing").count()
    applied = Company.query.filter_by(user_id=current_user.id, status="Applied").count()
    interview = Company.query.filter_by(user_id=current_user.id, status="Interview").count()
    offer = Company.query.filter_by(user_id=current_user.id, status="Offer").count()

    # ---------- Mock Interviews ----------
    mock_data = MockInterview.query.filter_by(
        user_id=current_user.id
    ).order_by(MockInterview.mock_date).all()

    return render_template(
        "analytics.html",
        easy=easy,
        medium=medium,
        hard=hard,
        completed=completed,
        progress=progress,
        pending=pending,
        planning=planning,
        preparing=preparing,
        applied=applied,
        interview=interview,
        offer=offer,
        mock_data=mock_data
    )