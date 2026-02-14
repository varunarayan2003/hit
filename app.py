import streamlit as st
import sqlite3
import pandas as pd

DB_NAME = "student_portal.db"

# ---------------- DATABASE ----------------

def get_conn():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

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
        password TEXT
    )
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
    )
    """)

    conn.commit()
    conn.close()


# ---------------- GRADE FUNCTION ----------------

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


# ---------------- SEED DATA ----------------

def seed_data():
    conn = get_conn()
    cur = conn.cursor()

    # Insert Student
    cur.execute("""
    INSERT OR IGNORE INTO students
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "506CS20188",
        "KOUSHIK N",
        "CSE",
        6,
        "A",
        "koushik@example.com",
        "9876543210",
        "password"
    ))

    # Delete old marks
    cur.execute("DELETE FROM marks WHERE usn=?", ("506CS20188",))

    real_marks_data = [

        # SEM 1
        (1,"15SC01M","ENGINEERING MATHS - I",20,77),
        (1,"15SC03S","APPLIED SCIENCE",20,80),
        (1,"15EC01T","CNCPT OF ELE & ELECTROENGG",14,53),
        (1,"15SC04P","APPLIED SCIENCE LAB",22,40),
        (1,"15EC02P","BASIC ELECTRONICS LAB",19,30),
        (1,"15CS11P","B C S LAB",21,40),

        # SEM 2
        (2,"15SC02M","ENGINEERING MATHS - II",20,75),
        (2,"15CP01E","COMMN SKILLS IN ENGLISH",23,81),
        (2,"15CS21T","DIGITAL & COMP FUNDMNTLS",25,85),
        (2,"15EC03P","DIGITAL ELECTRONICS LAB",22,44),
        (2,"15CS22P","BASIC WEB DESIGN LAB",22,44),
        (2,"15CS23P","MULTIMEDIA LAB",18,36),

        # SEM 3
        (3,"15CS31T","PROGRAMMING WITH C",22,95),
        (3,"15CS32T","COMPUTER ORG",19,64),
        (3,"15CS33T","DBMS",20,79),
        (3,"15CS34T","COMPUTER NETWORKS",23,73),
        (3,"15CS35P","PROGRAMM WITH C LAB",21,44),
        (3,"15CS36P","DBMS & GUI LAB",19,47),
        (3,"15CS37P","N/W ADMINSTRATION LAB",24,46),

        # SEM 4
        (4,"15CS41T","DATA STRUCTURES USING C",18,75),
        (4,"15CS42T","OOP WITH JAVA",18,75),
        (4,"15CS43T","OPERATING SYSTEM",19,77),
        (4,"15CS44T","PROFSNL ETHICS & INDIAN CONSTITUTION",22,83),
        (4,"15CS45P","DATA STRUCTURES LAB",23,46),
        (4,"15CS46P","OOP WITH JAVA LAB",24,48),
        (4,"15CS47P","LINUX LAB",24,48),

        # SEM 5
        (5,"15CS5IT","SOFTWARE ENGINEERING",21,78),
        (5,"15C5527","WEB",21,75),
        (5,"15C553T","ADA",22,75),
        (5,"15CS54T","GREEN COMPUTING",24,88),
        (5,"15C555P","WEB LAB",20,30),
        (5,"15C56P","ADR LAB",23,40),
        (5,"15C557P","PP LAB",21,47),

        # SEM 6
        (6,"15C861T","SOFTWARE TESTING",23,96),
        (6,"15CS62T","NETWORK SECURITY MANAGEMENT",23,79),
        (6,"SCS63T","INTERNET OF THINGS",21,72),
        (6,"156564P","SOFTWARE TESTING LAB",16,40),
        (6,"15CS65P","NETWORK SECURITY LAB",21,40),
        (6,"ISCS67P","PROJECT WORK - II",20,35),
    ]

    for sem, code, name, internal, external in real_marks_data:
        total = internal + external
        grade = calculate_grade(total)
        result = "PASS" if total >= 40 else "FAIL"

        cur.execute("""
        INSERT INTO marks
        (usn, semester, subject_code, subject_name, internal, external, total, grade, result)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            "506CS20188",
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


# ---------------- LOGIN ----------------

def login():
    st.title("🎓 Student Login")

    usn = st.text_input("USN")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM students WHERE usn=? AND password=?",
            (usn, password)
        )
        user = cur.fetchone()
        conn.close()

        if user:
            st.session_state["usn"] = usn
            st.rerun()
        else:
            st.error("Invalid USN or Password")


# ---------------- DASHBOARD ----------------

def dashboard():
    usn = st.session_state["usn"]
    conn = get_conn()

    student = pd.read_sql("SELECT * FROM students WHERE usn=?", conn, params=(usn,))
    marks = pd.read_sql("SELECT * FROM marks WHERE usn=?", conn, params=(usn,))
    conn.close()

    st.title("🎓 Student Dashboard")

    st.subheader(student.loc[0, "name"])
    st.write("**USN:**", usn)
    st.write("**Branch:**", student.loc[0, "branch"])
    st.write("**Email:**", student.loc[0, "email"])

    st.markdown("---")

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

    if st.button("Logout"):
        del st.session_state["usn"]
        st.rerun()


# ---------------- MAIN ----------------

init_db()
seed_data()

if "usn" not in st.session_state:
    login()
else:
    dashboard()
