import streamlit as st
import sqlite3
import pandas as pd
import os

DB_NAME = "student_portal.db"

# -----------------------------
# DATABASE CONNECTION
# -----------------------------
def get_conn():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

# -----------------------------
# CREATE TABLES
# -----------------------------
def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        usn TEXT PRIMARY KEY,
        name TEXT,
        branch TEXT,
        semester INTEGER,
        section TEXT,
        email TEXT,
        phone TEXT,
        password TEXT,
        photo TEXT
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS marks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usn TEXT,
        semester INTEGER,
        subject_code TEXT,
        subject_name TEXT,
        internal INTEGER,
        external INTEGER,
        total INTEGER,
        grade TEXT,
        result TEXT
    );
    """)

    conn.commit()
    conn.close()

# -----------------------------
# GRADE FUNCTION
# -----------------------------
def calculate_grade(total):
    if total >= 90:
        return "S"
    elif total >= 80:
        return "A"
    elif total >= 70:
        return "B"
    elif total >= 60:
        return "C"
    elif total >= 50:
        return "D"
    else:
        return "F"

# -----------------------------
# INSERT REAL DATA (FROM MARKS CARDS)
# -----------------------------
def seed_data():
    conn = get_conn()
    cur = conn.cursor()

    # Avoid duplicate insert
    cur.execute("SELECT * FROM students WHERE usn=?", ("506CS22058",))
    if cur.fetchone():
        conn.close()
        return

    # Student
    cur.execute("""
    INSERT INTO students
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "506CS22058",
        "HEMANTH GOWDA S",
        "CSE",
        6,
        "A",
        "hemanth@example.com",
        "9876543210",
        "password",
        "photo.png"
    ))

    data = [

    # ---------- SEM 1 ----------
    (1,"15SC01M","ENGINEERING MATHS 1",20,65),
    (1,"15SC03S","APPLIED SCIENCE",19,80),
    (1,"15EC01T","ELE & ELECTRO ENG",15,50),
    (1,"15SC04P","APPLIED SCIENCE LAB",20,40),
    (1,"15EC02P","ELECTRONICS LAB",19,30),
    (1,"15CS11P","BCS LAB",22,30),

    # ---------- SEM 2 ----------
    (2,"15SC02M","ENG MATHS II",23,75),
    (2,"15SC01E","COMMUNICATION ENGLISH",20,84),
    (2,"15EC01T","DIGITAL FUNDAMENTALS",19,55),
    (2,"15SC04P","DIGITAL ELECTRONICS LAB",22,43),
    (2,"15EC02P","WEB DESIGN LAB",19,35),
    (2,"15CS11P","MULTIMEDIA LAB",22,36),

    # ---------- SEM 3 ----------
    (3,"15CS31T","PROGRAMMING WITH C",23,95),
    (3,"15CS32T","COMPUTER ORGANIZATION",19,55),
    (3,"15CS33T","DBMS",20,78),
    (3,"15CS34T","COMPUTER NETWORKS",23,74),
    (3,"15CS35P","C LAB",21,44),
    (3,"15CS36P","DBMS LAB",19,35),
    (3,"15CS37P","NETWORK LAB",22,46),

    # ---------- SEM 4 ----------
    (4,"15CS41T","DSA WITH C",18,75),
    (4,"15CS42T","OOP WITH JAVA",18,75),
    (4,"15CS43T","OPERATING SYSTEM",19,77),
    (4,"15CS44T","PROFESSIONAL ETHICS",22,83),
    (4,"15CS45P","DSA LAB",23,46),
    (4,"15CS46P","JAVA LAB",24,48),
    (4,"15CS47P","LINUX LAB",24,48),

    # ---------- SEM 5 ----------
    (5,"15CS51T","SOFTWARE ENGINEERING",21,81),
    (5,"15CS52T","WEB",22,65),
    (5,"15CS53T","ADA",19,74),
    (5,"15CS54T","GREEN COMPUTING",24,84),
    (5,"15CS55P","ADA LAB",23,41),
    (5,"15CS56P","WEB LAB",21,45),
    (5,"15CS57P","PP LAB",22,40),

    # ---------- SEM 6 ----------
    (6,"15CS61T","SOFTWARE TESTING",24,96),
    (6,"15CS62T","NETWORK SECURITY",24,69),
    (6,"15CS63T","IOT",20,77),
    (6,"15CS64P","TESTING LAB",17,41),
    (6,"15CS65P","SECURITY LAB",21,40),
    (6,"15CS66P","PROJECT WORK",22,35),
    ]

    for sem, code, name, internal, external in data:
        total = internal + external
        grade = calculate_grade(total)
        result = "PASS" if total >= 40 else "FAIL"

        cur.execute("""
        INSERT INTO marks
        (usn, semester, subject_code, subject_name, internal, external, total, grade, result)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "506CS22058",
            sem,
            code,
            name,
            internal,
            external,
            total,
            grade,
            result
        ))

    conn.commit()
    conn.close()

# -----------------------------
# LOGIN
# -----------------------------
def login():
    st.title("🎓 Student Login")

    usn = st.text_input("USN")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT * FROM students WHERE usn=? AND password=?", (usn, password))
        user = cur.fetchone()
        conn.close()

        if user:
            st.session_state["usn"] = usn
            st.rerun()
        else:
            st.error("Invalid USN or Password")

# -----------------------------
# DASHBOARD
# -----------------------------
def dashboard():
    usn = st.session_state["usn"]
    conn = get_conn()

    student = pd.read_sql("SELECT * FROM students WHERE usn=?", conn, params=(usn,))
    marks = pd.read_sql("SELECT * FROM marks WHERE usn=?", conn, params=(usn,))
    conn.close()

    st.title("🎓 Student Dashboard")

    # Photo
    if os.path.exists("photo.png"):
        st.image("photo.png", width=150)

    st.subheader(student.loc[0, "name"])
    st.write("USN:", usn)
    st.write("Branch:", student.loc[0, "branch"])

    semesters = sorted(marks["semester"].unique())
    selected_sem = st.selectbox("Select Semester", semesters)

    sem_data = marks[marks["semester"] == selected_sem]

    st.dataframe(
        sem_data[["subject_code","subject_name","internal","external","total","grade","result"]],
        use_container_width=True
    )

    sgpa = round(sem_data["total"].mean() / 10, 2)
    cgpa = round(marks["total"].mean() / 10, 2)

    st.success(f"SGPA: {sgpa}")
    st.success(f"CGPA: {cgpa}")

# -----------------------------
# MAIN
# -----------------------------
init_db()
seed_data()

if "usn" not in st.session_state:
    login()
else:
    dashboard()