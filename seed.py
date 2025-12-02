from app import db, Department, FacultyCoordinator, Student, Company, Employer, Position, Resume, Application, Offer
from app import app
from datetime import datetime

with app.app_context():
    print("Resetting database...")
    db.drop_all()
    db.create_all()

    dept = Department(name="Computer Science")
    db.session.add(dept)
    db.session.commit()

    faculty = FacultyCoordinator(
        full_name="Dr. Medjahed",
        email="medjahed@umich.edu",
        department_id=dept.department_id
    )
    db.session.add(faculty)
    db.session.commit()

    student = Student(
        full_name="Ali Ramadan",
        email="ali@student.com",
        phone="555-1234",
        major="Computer Science",
        credits_in_major=45,
        gpa=3.7,
        start_term="Fall 2024",
        is_transfer=False,
        completed_semesters=3,
        department_id=dept.department_id
    )
    db.session.add(student)
    db.session.commit()

    resume = Resume(
        student_id=student.student_id,
        file_url="https://example.com/resume.pdf"
    )
    db.session.add(resume)
    db.session.commit()

    company = Company(
        name="TechCorp",
        location="Detroit, MI",
        website="https://techcorp.com"
    )
    db.session.add(company)
    db.session.commit()

    employer = Employer(
        company_id=company.company_id,
        full_name="Sarah Johnson",
        email="sarah@techcorp.com",
        phone="555-5678"
    )
    db.session.add(employer)
    db.session.commit()

    position = Position(
        employer_id=employer.employer_id,
        title="Software Engineering Co-Op",
        description="Backend work in Python/Flask.",
        weeks=12,
        hours_per_week=20,
        location="Hybrid",
        majors_of_interest="Computer Science",
        required_skills="Python, SQL",
        preferred_skills="Flask"
    )
    db.session.add(position)
    db.session.commit()

    application = Application(
        student_id=student.student_id,
        position_id=position.position_id,
        applied_at=datetime.utcnow(),
        status="Submitted"
    )
    db.session.add(application)
    db.session.commit()

    offer = Offer(
        position_id=position.position_id,
        selected_student_id=student.student_id,
        offer_letter_url="https://example.com/offer.pdf"
    )
    db.session.add(offer)
    db.session.commit()

    print("Database seeded successfully!")
