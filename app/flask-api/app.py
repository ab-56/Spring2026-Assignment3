from flask import Flask, jsonify, request
import mysql.connector
import os
import time

app = Flask(__name__)

REQUIRED_SKILLS = ["Python", "Git", "Docker", "Linux", "Kubernetes", "Cloud", "SQL"]


def get_db_connection():
    max_retries = 30
    for i in range(max_retries):
        try:
            conn = mysql.connector.connect(
                host=os.environ.get("DB_HOST", "mysql"),
                user=os.environ.get("DB_USER", "flaskuser"),
                password=os.environ.get("DB_PASSWORD", "flaskpass"),
                database=os.environ.get("DB_NAME", "flaskdb")
            )
            return conn
        except mysql.connector.Error:
            if i < max_retries - 1:
                time.sleep(2)
            else:
                raise


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            department VARCHAR(255),
            semester VARCHAR(50),
            cgpa FLOAT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS skills (
            id INT AUTO_INCREMENT PRIMARY KEY,
            skill_name VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS internships (
            id INT AUTO_INCREMENT PRIMARY KEY,
            company VARCHAR(255) NOT NULL,
            position VARCHAR(255) NOT NULL,
            status VARCHAR(100) NOT NULL,
            applied_date VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()


@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "service": "CareerPilot AI",
        "version": "bonus-v1"
    }), 200


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "app": "CareerPilot AI",
        "message": "AI-powered career readiness and internship tracking API",
        "endpoints": [
            "/health",
            "/api/student",
            "/api/skills",
            "/api/internships",
            "/api/readiness",
            "/api/recommendations"
        ]
    }), 200


@app.route("/api/student", methods=["POST"])
def create_student():
    data = request.get_json()

    if not data or "name" not in data:
        return jsonify({"error": "Student name is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO students (name, department, semester, cgpa)
        VALUES (%s, %s, %s, %s)
        """,
        (
            data["name"],
            data.get("department", ""),
            data.get("semester", ""),
            data.get("cgpa", 0)
        )
    )

    conn.commit()
    student_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return jsonify({
        "id": student_id,
        "name": data["name"],
        "department": data.get("department", ""),
        "semester": data.get("semester", ""),
        "cgpa": data.get("cgpa", 0)
    }), 201


@app.route("/api/student", methods=["GET"])
def get_students():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM students ORDER BY created_at DESC")
    students = cursor.fetchall()

    cursor.close()
    conn.close()

    for student in students:
        student["created_at"] = student["created_at"].strftime("%Y-%m-%d %H:%M:%S")

    return jsonify(students), 200


@app.route("/api/skills", methods=["POST"])
def add_skill():
    data = request.get_json()

    if not data or "skill_name" not in data:
        return jsonify({"error": "skill_name is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO skills (skill_name) VALUES (%s)",
        (data["skill_name"],)
    )

    conn.commit()
    skill_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return jsonify({
        "id": skill_id,
        "skill_name": data["skill_name"]
    }), 201


@app.route("/api/skills", methods=["GET"])
def get_skills():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM skills ORDER BY created_at DESC")
    skills = cursor.fetchall()

    cursor.close()
    conn.close()

    for skill in skills:
        skill["created_at"] = skill["created_at"].strftime("%Y-%m-%d %H:%M:%S")

    return jsonify(skills), 200


@app.route("/api/internships", methods=["POST"])
def add_internship():
    data = request.get_json()

    required_fields = ["company", "position", "status"]

    if not data:
        return jsonify({"error": "JSON body is required"}), 400

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO internships (company, position, status, applied_date)
        VALUES (%s, %s, %s, %s)
        """,
        (
            data["company"],
            data["position"],
            data["status"],
            data.get("applied_date", "")
        )
    )

    conn.commit()
    internship_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return jsonify({
        "id": internship_id,
        "company": data["company"],
        "position": data["position"],
        "status": data["status"],
        "applied_date": data.get("applied_date", "")
    }), 201


@app.route("/api/internships", methods=["GET"])
def get_internships():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM internships ORDER BY created_at DESC")
    internships = cursor.fetchall()

    cursor.close()
    conn.close()

    for internship in internships:
        internship["created_at"] = internship["created_at"].strftime("%Y-%m-%d %H:%M:%S")

    return jsonify(internships), 200


@app.route("/api/readiness", methods=["GET"])
def career_readiness():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT skill_name FROM skills")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    student_skills = [row["skill_name"].lower() for row in rows]
    matched = []

    for skill in REQUIRED_SKILLS:
        if skill.lower() in student_skills:
            matched.append(skill)

    readiness_score = int((len(matched) / len(REQUIRED_SKILLS)) * 100)
    missing_skills = [skill for skill in REQUIRED_SKILLS if skill not in matched]

    return jsonify({
        "required_skills": REQUIRED_SKILLS,
        "matched_skills": matched,
        "missing_skills": missing_skills,
        "career_readiness_score": readiness_score
    }), 200


@app.route("/api/recommendations", methods=["GET"])
def recommendations():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT skill_name FROM skills")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    student_skills = [row["skill_name"].lower() for row in rows]
    recommendations_list = []

    for skill in REQUIRED_SKILLS:
        if skill.lower() not in student_skills:
            recommendations_list.append(f"Improve your {skill} skill to increase career readiness.")

    if not recommendations_list:
        recommendations_list.append("You have strong readiness for internships and placements.")

    return jsonify({
        "recommendations": recommendations_list
    }), 200


@app.route("/api/stats", methods=["GET"])
def stats():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT COUNT(*) AS total_skills FROM skills")
    skills_count = cursor.fetchone()["total_skills"]

    cursor.execute("SELECT COUNT(*) AS total_applications FROM internships")
    applications_count = cursor.fetchone()["total_applications"]

    cursor.execute("SELECT status, COUNT(*) AS count FROM internships GROUP BY status")
    status_counts = cursor.fetchall()

    cursor.close()
    conn.close()

    return jsonify({
        "total_skills": skills_count,
        "total_applications": applications_count,
        "application_status_summary": status_counts
    }), 200


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
