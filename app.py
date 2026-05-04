import streamlit as st
import sqlite3
import os
import pandas as pd

DB_NAME = "student_portal.db"

# --------------------------
# GRADE FUNCTION
# --------------------------
def calculate_grade(total):
    if total >= 90: return "S"
    elif total >= 80: return "A"
    elif total >= 70: return "B"
    elif total >= 60: return "C"
    elif total >= 50: return "D"
    else: return "F"

# --------------------------
# CREATE DATABASE
# --------------------------
def create_database():
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # STUDENT TABLE
    cur.execute("""
    CREATE TABLE students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usn TEXT UNIQUE,
        name TEXT,
        branch TEXT,
        semester INTEGER,
        section TEXT,
        email TEXT,
        phone TEXT,
        password TEXT
    )
    """)

    # MARKS TABLE
    cur.execute("""
    CREATE TABLE marks (
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

    # INSERT STUDENT LOGIN DATA
    cur.execute("""
    INSERT INTO students VALUES (NULL,?,?,?,?,?,?,?,?)
    """, (
        "506EC21028",
        "BALAJI K N",
        "ECE",
        6,
        "A",
        "balaji@example.com",
        "9876543210",
        "1234"   # PASSWORD
    ))

    # ALL SEM MARKS
    marks_data = [

    # SEM 1
    (1,"21EC01M","Engineering Maths I",20,65),
    (1,"21EC01T","Applied Science",19,80),
    (1,"21EC01T","Basic Electrical",15,50),

    # SEM 2
    (2,"21EC02M","Engineering Maths II",23,75),
    (2,"21EC02E","English",20,84),

    # SEM 3
    (3,"21EC31T","Analog Circuits",23,95),

    # SEM 4
    (4,"21EC41T","Microcontroller",18,75),

    # SEM 5
    (5,"21EC51T","Entrepreneurship",21,81),

    # SEM 6
    (6,"15CS61T","Industrial Automation",24,96),
    ]

    for sem, code, name, internal, external in marks_data:
        total = internal + external
        grade = calculate_grade(total)
        result = "PASS"

        cur.execute("""
        INSERT INTO marks
        (usn, semester, subject_code, subject_name,
        internal, external, total, grade, result)
        VALUES (?,?,?,?,?,?,?,?,?)
        """, (
            "506EC21028",
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

# --------------------------
# LOGIN FUNCTION
# --------------------------
def login(usn, password):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("SELECT * FROM students WHERE usn=? AND password=?", (usn, password))
    user = cur.fetchone()

    conn.close()
    return user

# --------------------------
# GET MARKS
# --------------------------
def get_marks(usn, sem):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(
        "SELECT subject_name, internal, external, total, grade FROM marks WHERE usn=? AND semester=?",
        conn,
        params=(usn, sem)
    )
    conn.close()
    return df

# --------------------------
# SESSION STATE
# --------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --------------------------
# UI
# --------------------------
st.title("🎓 Student Portal")

# CREATE DB BUTTON
if st.button("Create Database"):
    create_database()
    st.success("Database Created!")

# --------------------------
# LOGIN PAGE
# --------------------------
if not st.session_state.logged_in:

    st.subheader("🔐 Student Login")

    usn = st.text_input("Enter USN")
    password = st.text_input("Enter Password", type="password")

    if st.button("Login"):
        user = login(usn, password)

        if user:
            st.session_state.logged_in = True
            st.session_state.usn = usn
            st.success("Login Successful!")
        else:
            st.error("Invalid USN or Password")

# --------------------------
# DASHBOARD
# --------------------------
else:
    st.success(f"Welcome {st.session_state.usn}")

    if st.button("Logout"):
        st.session_state.logged_in = False

    sem = st.selectbox("Select Semester", [1,2,3,4,5,6])

    if st.button("View Marks"):
        df = get_marks(st.session_state.usn, sem)
        st.dataframe(df)

        if not df.empty:
            total = df["total"].sum()
            avg = total / len(df)

            st.info(f"Total Marks: {total}")
            st.success(f"Average: {avg:.2f}")