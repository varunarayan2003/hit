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

    # TABLES
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
        password TEXT,
        photo_url TEXT
    )
    """)

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

    # INSERT STUDENT
    cur.execute("""
    INSERT INTO students VALUES (NULL,?,?,?,?,?,?,?,?,?)
    """, (
        "506EC21028",
        "BALAJI K N",
        "ECE",
        6,
        "A",
        "balaji@example.com",
        "9876543210",
        "password",
        ""
    ))

    # --------------------------
    # ALL SEM MARKS
    # --------------------------
    marks_data = [

    # SEM 1
    (1,"21EC01M","Engineering Maths I",20,65),
    (1,"21EC01T","Applied Science",19,80),
    (1,"21EC01T","Basic Electrical & Electronics",15,50),
    (1,"21EC01P","Applied Science Lab",20,40),
    (1,"21EC01P","BEEE Lab",19,30),
    (1,"21EC01P","Computer Concepts Lab",22,30),

    # SEM 2
    (2,"21EC02M","Engineering Maths II",23,75),
    (2,"21EC02E","Communication English",20,84),
    (2,"21EC02T","Semiconductor Devices",19,55),
    (2,"21EC02P","Semiconductor Lab",22,43),
    (2,"21EC02P","Digital Electronics Lab",19,35),
    (2,"21EC12P","Maths Simulation Lab",22,36),

    # SEM 3
    (3,"21EC31T","Analog Circuits",23,95),
    (3,"21EC32T","Digital Electronics",19,55),
    (3,"21EC33T","EMI",20,78),
    (3,"21EC34T","Analog Communication",23,74),
    (3,"21EC35P","Analog & Comm Lab",21,44),
    (3,"21EC36P","Digital Electronics Lab",19,35),
    (3,"21EC37P","C Lab",22,46),

    # SEM 4
    (4,"21EC41T","Microcontroller & Applications",18,75),
    (4,"21EC42T","Digital Communication",18,75),
    (4,"21EC43T","Data Communication & Networks",19,77),
    (4,"21EC44T","Professional Ethics",22,83),
    (4,"21EC45P","DC & Networking Lab",23,46),
    (4,"21EC46P","Practice Lab",24,48),
    (4,"21EC47P","Microcontroller Lab",24,48),

    # SEM 5
    (5,"21EC51T","OM & Entrepreneurship",21,81),
    (5,"21EC52T","ARM Controller",22,65),
    (5,"21EC53T","AD Communication",19,74),
    (5,"21EC54T","Applications of ECE",24,84),
    (5,"21EC55P","Applications Lab",23,41),
    (5,"21EC56P","PCB Design & FabLab",21,45),
    (5,"21EC57P","Electrical Servicing",22,40),

    # SEM 6
    (6,"21EC61T","Industrial Automation",24,96),
    (6,"21EC62T","Embedded Systems",24,69),
    (6,"21EC63T","Medical Electronics",20,77),
    (6,"21EC64P","Automation Lab",17,41),
    (6,"21EC65P","Verilog Lab",21,40),
    (6,"21EC66P","Project Work II",22,35),
    ]

    # INSERT MARKS
    for sem, code, name, internal, external in marks_data:
        total = internal + external
        grade = calculate_grade(total)
        result = "PASS" if total >= 40 else "FAIL"

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
# FETCH DATA
# --------------------------
def get_marks(semester):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query(
        "SELECT subject_code, subject_name, internal, external, total, grade FROM marks WHERE semester=?",
        conn,
        params=(semester,)
    )
    conn.close()
    return df

# --------------------------
# STREAMLIT UI
# --------------------------
st.set_page_config(page_title="Student Portal", layout="wide")

st.title("🎓 Student Portal Dashboard")

# BUTTON TO CREATE DB
if st.button("Create Database"):
    create_database()
    st.success("✅ Database created successfully!")

# SEMESTER SELECT
st.subheader("📚 View Marks")

sem = st.selectbox("Select Semester", [1,2,3,4,5,6])

if st.button("Show Results"):
    if not os.path.exists(DB_NAME):
        st.error("⚠️ Please create database first!")
    else:
        df = get_marks(sem)
        st.dataframe(df, use_container_width=True)

        total_marks = df["total"].sum()
        percentage = total_marks / len(df)

        st.success(f"🎯 Total Marks: {total_marks}")
        st.info(f"📊 Average: {percentage:.2f}")
