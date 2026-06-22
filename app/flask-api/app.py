from flask import Flask, jsonify, request
import mysql.connector
import os
import time

app = Flask(__name__)

REQUIRED_SKILLS = [
    "Python",
    "Git",
    "Docker",
    "Linux",
    "Kubernetes",
    "Cloud",
    "SQL"
]


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
            student_id INT,
            skill_name VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS internships (
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_id INT,
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
        "version": "v2"
    })


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "app": "CareerPilot AI",
        "message": "AI-powered career readiness platform",
        "endpoints": [
            "/api/student",
            "/api/skills",
            "/api/internships",
            "/api/readiness/<student_id>",
            "/api/recommendations/<student_id>",
            "/api/stats"
        ]
    })


@app.route("/api/student", methods=["POST"])
def create_student():

    data = request.get_json()

    if not data or "name" not in data:
        return jsonify({
            "error": "Student name is required"
        }), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO students
        (name, department, semester, cgpa)
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

    cursor.execute(
        "SELECT * FROM students ORDER BY id"
    )

    students = cursor.fetchall()

    cursor.close()
    conn.close()

    for student in students:
        student["created_at"] = student["created_at"].strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    return jsonify(students)


@app.route("/api/skills", methods=["POST"])
def add_skill():

    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON required"}), 400

    if "student_id" not in data:
        return jsonify({"error": "student_id required"}), 400

    if "skill_name" not in data:
        return jsonify({"error": "skill_name required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO skills
        (student_id, skill_name)
        VALUES (%s, %s)
        """,
        (
            data["student_id"],
            data["skill_name"]
        )
    )

    conn.commit()

    skill_id = cursor.lastrowid

    cursor.close()
    conn.close()

    return jsonify({
        "id": skill_id,
        "student_id": data["student_id"],
        "skill_name": data["skill_name"]
    }), 201


@app.route("/api/skills", methods=["GET"])
def get_skills():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT s.id,
               s.student_id,
               st.name AS student_name,
               s.skill_name,
               s.created_at
        FROM skills s
        JOIN students st
        ON s.student_id = st.id
        ORDER BY s.id
    """)

    skills = cursor.fetchall()

    cursor.close()
    conn.close()

    for skill in skills:
        skill["created_at"] = skill["created_at"].strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    return jsonify(skills)


@app.route("/api/internships", methods=["POST"])
def add_internship():

    data = request.get_json()

    required = [
        "student_id",
        "company",
        "position",
        "status"
    ]

    if not data:
        return jsonify({
            "error": "JSON required"
        }), 400

    for field in required:
        if field not in data:
            return jsonify({
                "error": f"{field} required"
            }), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO internships
        (student_id, company, position, status, applied_date)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            data["student_id"],
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
        "student_id": data["student_id"],
        "company": data["company"],
        "position": data["position"],
        "status": data["status"]
    }), 201


@app.route("/api/internships", methods=["GET"])
def get_internships():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT i.id,
               i.student_id,
               st.name AS student_name,
               i.company,
               i.position,
               i.status,
               i.applied_date,
               i.created_at
        FROM internships i
        JOIN students st
        ON i.student_id = st.id
        ORDER BY i.id
    """)

    internships = cursor.fetchall()

    cursor.close()
    conn.close()

    for internship in internships:
        internship["created_at"] = internship["created_at"].strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    return jsonify(internships)


@app.route("/api/readiness/<int:student_id>", methods=["GET"])
def career_readiness(student_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT skill_name
        FROM skills
        WHERE student_id = %s
        """,
        (student_id,)
    )

    rows = cursor.fetchall()

    student_skills = [
        row["skill_name"].lower()
        for row in rows
    ]

    cursor.execute(
        """
        SELECT name
        FROM students
        WHERE id = %s
        """,
        (student_id,)
    )

    student = cursor.fetchone()

    cursor.close()
    conn.close()

    matched = []

    for skill in REQUIRED_SKILLS:
        if skill.lower() in student_skills:
            matched.append(skill)

    missing = [
        skill
        for skill in REQUIRED_SKILLS
        if skill not in matched
    ]

    score = int(
        (len(matched) / len(REQUIRED_SKILLS)) * 100
    )

    return jsonify({
        "student": student["name"],
        "career_readiness_score": score,
        "matched_skills": matched,
        "missing_skills": missing
    })


@app.route("/api/recommendations/<int:student_id>", methods=["GET"])
def recommendations(student_id):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT skill_name
        FROM skills
        WHERE student_id = %s
        """,
        (student_id,)
    )

    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    student_skills = [
        row["skill_name"].lower()
        for row in rows
    ]

    recommendations_list = []

    for skill in REQUIRED_SKILLS:
        if skill.lower() not in student_skills:
            recommendations_list.append(
                f"Improve your {skill} skill."
            )

    if not recommendations_list:
        recommendations_list.append(
            "Excellent career readiness."
        )

    return jsonify({
        "student_id": student_id,
        "recommendations": recommendations_list
    })


@app.route("/api/stats", methods=["GET"])
def stats():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT COUNT(*) AS total_students FROM students"
    )

    total_students = cursor.fetchone()["total_students"]

    cursor.execute(
        "SELECT COUNT(*) AS total_skills FROM skills"
    )

    total_skills = cursor.fetchone()["total_skills"]

    cursor.execute(
        "SELECT COUNT(*) AS total_applications FROM internships"
    )

    total_applications = cursor.fetchone()["total_applications"]

    cursor.close()
    conn.close()

    return jsonify({
        "total_students": total_students,
        "total_skills": total_skills,
        "total_applications": total_applications
    })


if __name__ == "__main__":
    init_db()
    app.run(
        host="0.0.0.0",
        port=5000
    )
