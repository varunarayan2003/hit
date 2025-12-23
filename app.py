import streamlit as st
import sqlite3
import pandas as pd
import os

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
        password TEXT,
        photo TEXT
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
        result TEXT,
        UNIQUE(usn, semester, subject_code)
    )
    """)

    conn.commit()
    conn.close()

# ---------------- SEED DATA ----------------

def seed_data():
    conn = get_conn()
    cur = conn.cursor()

    # Student
    cur.execute("""
    INSERT OR IGNORE INTO students
    (usn, name, branch, semester, section, email, phone, password, photo)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "BCOM0057",
        "VENUGOPAL G",
        "B.COM",
        6,
        "A",
        "vg5690275@gmail.com",
        "6360611534",
        "venu@123",
        "venugopal.JPG"
    ))

    # Marks (ALL SEMESTERS)
    marks = [
        # SEM 1
        ("BCOM0057",1,"B.COM 1.1","FINANCIAL ACCOUNTING",18,45,63,"A","PASS"),
        ("BCOM0057",1,"B.COM 1.2","MANAGEMENT PRINCIPLES",20,60,80,"A","PASS"),
        ("BCOM0057",1,"B.COM 1.3","PRINCIPLES OF MARKETING",20,65,85,"A+","PASS"),
        ("BCOM0057",1,"B.COM 1.4","DIGITAL FLUENCY",18,50,68,"A","PASS"),
        ("BCOM0057",1,"B.COM 1.5","ACCOUNTING FOR EVERYONE",16,55,71,"A","PASS"),
        ("BCOM0057",1,"LANG I","LANGUAGE - I",23,59,82,"A+","PASS"),

        # SEM 2
        ("BCOM0057",2,"B.COM 2.1","ADVANCED FINANCIAL",18,50,68,"A","PASS"),
        ("BCOM0057",2,"B.COM 2.2","CORPORATE ADMINISTRATION",15,59,74,"A","PASS"),
        ("BCOM0057",2,"B.COM 2.3","BANKING LAW & PRACTICE",16,62,78,"A","PASS"),
        ("BCOM0057",2,"B.COM 2.4","ENVIRONMENTAL STUDIES",14,55,69,"A","PASS"),
        ("BCOM0057",2,"B.COM 2.5","INVESTING IN STOCK MARKETS",15,60,75,"A","PASS"),
        ("BCOM0057",2,"LANG II","LANGUAGE - II",22,50,72,"A","PASS"),

        # SEM 3
        ("BCOM0057",3,"B.COM 3.1","CORPORATE ACCOUNTING",15,50,65,"A","PASS"),
        ("BCOM0057",3,"B.COM 3.2","BUSINESS STATISTICS",21,45,66,"A","PASS"),
        ("BCOM0057",3,"B.COM 3.3","COST ACCOUNTING",18,60,78,"A","PASS"),
        ("BCOM0057",3,"B.COM 3.4","FINANCIAL EDUCATION",19,52,71,"A","PASS"),
        ("BCOM0057",3,"LANG III","LANGUAGE - III",20,50,70,"A","PASS"),
        ("BCOM0057",3,"SPORTS","SPORTS",21,54,75,"A","PASS"),

        # SEM 4
        ("BCOM0057",4,"B.COM 4.1","ADVANCED CORPORATE ACCOUNTING",17,50,67,"A","PASS"),
        ("BCOM0057",4,"B.COM 4.2","COSTING METHODS",22,45,67,"A","PASS"),
        ("BCOM0057",4,"B.COM 4.3","BUSINESS REGULATORY",20,42,62,"A","PASS"),
        ("BCOM0057",4,"B.COM 4.4","ARTIFICIAL INTELLIGENCE",19,52,71,"A","PASS"),
        ("BCOM0057",4,"B.COM 4.5","BUSINESS ETHICS",20,50,70,"A","PASS"),
        ("BCOM0057",4,"LANG IV","LANGUAGE - IV",21,59,80,"A+","PASS"),

        # SEM 5
        ("BCOM0057",5,"B.COM 5.1","MARKETING MANAGEMENT",19,55,74,"A","PASS"),
        ("BCOM0057",5,"B.COM 5.2","INCOME TAX",22,50,72,"A","PASS"),
        ("BCOM0057",5,"B.COM 5.3","CORPORATE GOVERNANCE",22,45,67,"A","PASS"),
        ("BCOM0057",5,"B.COM 5.4","AUDITING",14,52,66,"A","PASS"),
        ("BCOM0057",5,"B.COM 5.5","CORPORATE COMMUNICATION",18,55,68,"A","PASS"),
        ("BCOM0057",5,"B.COM 5.6","PROJECT - I",21,60,81,"A+","PASS"),

        # SEM 6
        ("BCOM0057",6,"B.COM 6.1","LAW",18,40,58,"B","PASS"),
        ("BCOM0057",6,"B.COM 6.2","ACCOUNTING & FINANCE",20,46,66,"A","PASS"),
        ("BCOM0057",6,"B.COM 6.3","TAXATION",22,52,74,"A","PASS"),
        ("BCOM0057",6,"B.COM 6.4","MANAGEMENT",15,58,73,"A","PASS"),
        ("BCOM0057",6,"B.COM 6.5","IT",20,55,75,"A","PASS"),
        ("BCOM0057",6,"B.COM 6.6","INTERNSHIP",21,62,83,"A+","PASS"),
    ]

    cur.executemany("""
    INSERT OR IGNORE INTO marks
    (usn, semester, subject_code, subject_name, internal, external, total, grade, result)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, marks)

    conn.commit()
    conn.close()

# ---------------- LOGIN ----------------

def login():
    st.title("🎓 Student Login")

    usn = st.text_input("USN", key="login_usn")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login", key="login_btn"):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "SELECT usn FROM students WHERE usn=? AND password=?",
            (usn, password)
        )
        row = cur.fetchone()
        conn.close()

        if row:
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

    photo = student.loc[0, "photo"]
    if photo and os.path.exists(photo):
        st.image(photo, width=150)

    st.subheader(student.loc[0, "name"])
    st.write("**USN:**", usn)
    st.write("**Branch:**", student.loc[0, "branch"])
    st.write("**Email:**", student.loc[0, "email"])

    st.markdown("---")

    marks["semester"] = marks["semester"].astype(int)
    semesters = sorted(marks["semester"].unique())

    selected_sem = st.selectbox(
        "Select Semester",
        semesters,
        key="semester_dropdown"
    )

    sem_data = marks[marks["semester"] == selected_sem]

    st.dataframe(
        sem_data[
            ["subject_code","subject_name","internal","external","total","grade","result"]
        ],
        use_container_width=True
    )

    sgpa = round(sem_data["total"].mean() / 10, 2)
    cgpa = round(marks["total"].mean() / 10, 2)

    st.success(f"SGPA: {sgpa}")
    st.success(f"CGPA: {cgpa}")

    if st.button("Logout", key="logout_btn"):
        del st.session_state["usn"]
        st.rerun()

# ---------------- MAIN ----------------

init_db()
seed_data()

if "usn" not in st.session_state:
    login()
else:
    dashboard()
