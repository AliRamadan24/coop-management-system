from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-key"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///coop.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# MODELS

class Department(db.Model):
    __tablename__ = "Departments"
    department_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class FacultyCoordinator(db.Model):
    __tablename__ = "FacultyCoordinators"
    faculty_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey("Departments.department_id"), nullable=False)
    department = db.relationship("Department", backref="faculty")

class Student(db.Model):
    __tablename__ = "Students"
    student_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    major = db.Column(db.String(100))
    credits_in_major = db.Column(db.Integer)
    gpa = db.Column(db.Float)
    start_term = db.Column(db.String(20))
    is_transfer = db.Column(db.Boolean, default=False)
    completed_semesters = db.Column(db.Integer)
    department_id = db.Column(db.Integer, db.ForeignKey("Departments.department_id"))
    department = db.relationship("Department", backref="students")

class Resume(db.Model):
    __tablename__ = "Resumes"
    resume_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("Students.student_id"), nullable=False)
    file_url = db.Column(db.String(255), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)
    student = db.relationship("Student", backref="resumes")

class Company(db.Model):
    __tablename__ = "Companies"
    company_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(150))
    website = db.Column(db.String(255))

class Employer(db.Model):
    __tablename__ = "Employers"
    employer_id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("Companies.company_id"), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    company = db.relationship("Company", backref="employers")

class Position(db.Model):
    __tablename__ = "Positions"
    position_id = db.Column(db.Integer, primary_key=True)
    employer_id = db.Column(db.Integer, db.ForeignKey("Employers.employer_id"), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    weeks = db.Column(db.Integer)
    hours_per_week = db.Column(db.Integer)
    location = db.Column(db.String(150))
    majors_of_interest = db.Column(db.String(255))
    required_skills = db.Column(db.String(255))
    preferred_skills = db.Column(db.String(255))
    employer = db.relationship("Employer", backref="positions")

class Application(db.Model):
    __tablename__ = "Applications"
    application_id = db.Column(db.Integer, primary_key=True)
    position_id = db.Column(db.Integer, db.ForeignKey("Positions.position_id"), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey("Students.student_id"), nullable=False)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default="Pending")
    student = db.relationship("Student", backref="applications")
    position = db.relationship("Position", backref="applications")

class Offer(db.Model):
    __tablename__ = "Offers"
    offer_id = db.Column(db.Integer, primary_key=True)
    position_id = db.Column(db.Integer, db.ForeignKey("Positions.position_id"), nullable=False)
    selected_student_id = db.Column(db.Integer, db.ForeignKey("Students.student_id"), nullable=False)
    offer_letter_url = db.Column(db.String(255))
    marked_pending_at = db.Column(db.DateTime, default=datetime.utcnow)
    position = db.relationship("Position", backref="offers")
    student = db.relationship("Student", backref="offers")

class CoOpSummary(db.Model):
    __tablename__ = "CoOpSummaries"
    summary_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("Students.student_id"), nullable=False)
    position_id = db.Column(db.Integer, db.ForeignKey("Positions.position_id"), nullable=False)
    text = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    student = db.relationship("Student", backref="coop_summaries")
    position = db.relationship("Position", backref="coop_summaries")

class Grade(db.Model):
    __tablename__ = "Grades"
    grade_id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("Students.student_id"), nullable=False)
    position_id = db.Column(db.Integer, db.ForeignKey("Positions.position_id"), nullable=False)
    grade_value = db.Column(db.String(5), nullable=False)
    graded_by = db.Column(db.Integer, db.ForeignKey("FacultyCoordinators.faculty_id"), nullable=False)
    graded_at = db.Column(db.DateTime, default=datetime.utcnow)
    student = db.relationship("Student", backref="grades")
    position = db.relationship("Position", backref="grades")
    faculty = db.relationship("FacultyCoordinator", backref="grades")

# HELPERS

def current_user():
    role = session.get("role")
    user_id = session.get("user_id")
    if not role or not user_id:
        return None, None

    if role == "student":
        return Student.query.get(user_id), role
    if role == "employer":
        return Employer.query.get(user_id), role
    if role == "faculty":
        return FacultyCoordinator.query.get(user_id), role

    return None, None

# LOGIN

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        role = request.form["role"]

        if role == "student":
            user = Student.query.filter_by(email=email).first()
        elif role == "employer":
            user = Employer.query.filter_by(email=email).first()
        else:
            user = FacultyCoordinator.query.filter_by(email=email).first()

        if not user:
            flash("User not found for that role.", "error")
            return redirect(url_for("login"))

        session["user_id"] = (
            user.student_id if role == "student" else
            user.employer_id if role == "employer" else
            user.faculty_id
        )
        session["role"] = role

        if role == "student": return redirect("/student/dashboard")
        if role == "employer": return redirect("/employer/dashboard")
        if role == "faculty": return redirect("/faculty/dashboard")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# STUDENT ROUTES

@app.route("/student/dashboard")
def student_dashboard():
    user, role = current_user()
    if role != "student":
        return redirect("/")

    employer_name = request.args.get("employer")
    major_filter = request.args.get("major")

    query = Position.query

    if employer_name:
        query = query.join(Employer).join(Company).filter(
            (Employer.full_name.contains(employer_name)) |
            (Company.name.contains(employer_name))
        )

    if major_filter:
        query = query.filter(Position.majors_of_interest.contains(major_filter))

    positions = query.all()
    applications = Application.query.filter_by(student_id=user.student_id).all()

    return render_template(
        "student_dashboard.html",
        student=user,
        positions=positions,
        applications=applications
    )

@app.route("/student/apply/<int:position_id>", methods=["POST"])
def apply_to_position(position_id):
    user, role = current_user()
    if role != "student":
        return redirect("/")

    existing = Application.query.filter_by(
        student_id=user.student_id,
        position_id=position_id
    ).first()

    if existing:
        flash("You already applied to this position.", "error")
    else:
        new_app = Application(
            student_id=user.student_id,
            position_id=position_id,
            applied_at=datetime.utcnow(),
            status="Submitted"
        )
        db.session.add(new_app)
        db.session.commit()
        flash("Application Submitted Successfully!", "success")

    return redirect("/student/dashboard")

# STUDENT SUMMARY (THE MISSING ROUTE)

@app.route("/student/summary", methods=["GET", "POST"])
def submit_summary():
    user, role = current_user()
    if role != "student":
        return redirect("/")

    if request.method == "POST":
        position_id = int(request.form.get("position_id"))
        text = request.form.get("text")

        summary = CoOpSummary(
            student_id=user.student_id,
            position_id=position_id,
            text=text,
            submitted_at=datetime.utcnow()
        )
        db.session.add(summary)
        db.session.commit()

        flash("Co-Op Summary Submitted!", "success")
        return redirect("/student/dashboard")

    offers = Offer.query.filter_by(selected_student_id=user.student_id).all()

    return render_template("student_summary.html", offers=offers, student=user)

# EMPLOYER ROUTES

@app.route("/employer/dashboard", methods=["GET", "POST"])
def employer_dashboard():
    user, role = current_user()
    if role != "employer":
        return redirect("/")

    if request.method == "POST":
        position = Position(
            employer_id=user.employer_id,
            title=request.form["title"],
            description=request.form["description"],
            weeks=request.form["weeks"],
            hours_per_week=request.form["hours_per_week"],
            location=request.form["location"],
            majors_of_interest=request.form["majors_of_interest"],
            required_skills=request.form["required_skills"],
            preferred_skills=request.form["preferred_skills"]
        )
        db.session.add(position)
        db.session.commit()
        flash("Position posted!", "success")

    positions = Position.query.filter_by(employer_id=user.employer_id).all()
    return render_template("employer_dashboard.html", employer=user, positions=positions)

# FACULTY ROUTES

@app.route("/faculty/dashboard")
def faculty_dashboard():
    user, role = current_user()
    if role != "faculty":
        return redirect("/")

    students = Student.query.filter_by(department_id=user.department_id).all()
    return render_template("faculty_dashboard.html", faculty=user, students=students)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
