import streamlit as st
import sqlite3
from pathlib import Path
import pandas as pd
import random

DB_NAME = "student_portal.db"


# ---------- DATABASE SETUP ----------

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def init_db():
    """Create tables and seed sample data if empty."""
    conn = get_connection()
    cur = conn.cursor()

    # Create students table
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
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
        );
        """
    )

    # Create marks table
    cur.execute(
        """
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
            FOREIGN KEY(usn) REFERENCES students(usn)
        );
        """
    )

    # Check if there are already students
    cur.execute("SELECT COUNT(*) FROM students;")
    count = cur.fetchone()[0]

    if count == 0:
        seed_sample_data(cur)

    conn.commit()
    conn.close()


def seed_sample_data(cur):
    """Insert 30 sample students and some marks for them."""
    branches = ["CSE", "ECE", "ME", "EEE", "CIVIL"]
    sections = ["A", "B"]

    # Insert 30 students
    for i in range(1, 31):
        usn = f"USN{i:03d}"
        name = f"Student {i}"
        branch = random.choice(branches)
        semester = random.randint(1, 8)
        section = random.choice(sections)
        email = f"student{i}@college.edu"
        phone = f"9{random.randint(100000000, 999999999)}"
        password = "password"  # default password for demo
        photo_url = ""  # can be used later for real photos

        cur.execute(
            """
            INSERT INTO students (usn, name, branch, semester, section, email, phone, password, photo_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            (usn, name, branch, semester, section, email, phone, password, photo_url),
        )

        # Add marks for 2 semesters (for demo)
        for sem in [1, 2]:
            subjects = [
                ("MAT" + str(sem), f"Mathematics {sem}"),
                ("PHY" + str(sem), f"Physics {sem}"),
                ("CS" + str(sem), f"Computer Science {sem}"),
                ("ELE" + str(sem), f"Electronics {sem}"),
                ("ENG" + str(sem), f"English {sem}"),
            ]

            for code, name_sub in subjects:
                internal = random.randint(15, 30)
                external = random.randint(10, 70)
                total = internal + external

                if total >= 90:
                    grade = "S"
                elif total >= 80:
                    grade = "A"
                elif total >= 70:
                    grade = "B"
                elif total >= 60:
                    grade = "C"
                elif total >= 50:
                    grade = "D"
                else:
                    grade = "F"

                result = "PASS" if total >= 50 else "FAIL"

                cur.execute(
                    """
                    INSERT INTO marks (usn, semester, subject_code, subject_name, internal, external, total, grade, result)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
                    """,
                    (usn, sem, code, name_sub, internal, external, total, grade, result),
                )


# ---------- DATA ACCESS FUNCTIONS ----------

def get_student_by_login(usn, password):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT usn, name, branch, semester, section, email, phone, photo_url
        FROM students
        WHERE usn = ? AND password = ?;
        """,
        (usn, password),
    )
    row = cur.fetchone()
    conn.close()
    return row


def get_student_by_usn(usn):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT usn, name, branch, semester, section, email, phone, photo_url
        FROM students
        WHERE usn = ?;
        """,
        (usn,),
    )
    row = cur.fetchone()
    conn.close()
    return row


def get_semesters_for_student(usn):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT DISTINCT semester
        FROM marks
        WHERE usn = ?
        ORDER BY semester;
        """,
        (usn,),
    )
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows]


def get_marks_for_student_sem(usn, semester):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT subject_code, subject_name, internal, external, total, grade, result
        FROM marks
        WHERE usn = ? AND semester = ?
        ORDER BY subject_code;
        """,
        (usn, semester),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_overall_stats(usn):
    """Calculate overall CGPA-like value and pass/fail."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT total, result
        FROM marks
        WHERE usn = ?;
        """,
        (usn,),
    )
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return None, None

    totals = [r[0] for r in rows]
    results = [r[1] for r in rows]

    avg_total = sum(totals) / len(totals)
    # Fake CGPA calculation: scale 0-100 to 0-10
    cgpa = round(avg_total / 10, 2)
    overall_result = "FAIL" if "FAIL" in results else "PASS"

    return cgpa, overall_result


# ---------- UI COMPONENTS ----------

def show_login():
    st.title("🎓 Student Portal Login")

    with st.form("login_form"):
        usn = st.text_input("USN / Student ID")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")

    if submitted:
        if not usn or not password:
            st.error("Please enter both USN and password.")
            return

        student = get_student_by_login(usn.strip(), password.strip())
        if student:
            st.session_state["logged_in"] = True
            st.session_state["usn"] = student[0]
            st.experimental_rerun()
        else:
            st.error("Invalid USN or password.")


def show_dashboard():
    usn = st.session_state.get("usn")
    student = get_student_by_usn(usn)

    if not student:
        st.error("Student not found.")
        return

    s_usn, s_name, s_branch, s_sem, s_section, s_email, s_phone, s_photo = student

    # Top bar
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🎓 Student Dashboard")
    with col2:
        if st.button("Logout"):
            st.session_state.clear()
            st.experimental_rerun()

    st.markdown("---")

    # Student Profile
    col1, col2 = st.columns([1, 3])
    with col1:
        # Placeholder photo
        st.image(
            "https://via.placeholder.com/150?text=Photo",
            caption=s_name,
            use_column_width=True,
        )
    with col2:
        st.subheader(s_name)
        st.write(f"**USN:** {s_usn}")
        st.write(f"**Branch:** {s_branch}")
        st.write(f"**Current Semester:** {s_sem}")
        st.write(f"**Section:** {s_section}")
        st.write(f"**Email:** {s_email}")
        st.write(f"**Phone:** {s_phone}")

    st.markdown("---")

    # Semester-wise marks
    st.subheader("📚 Semester-wise Marks Card")

    semesters = get_semesters_for_student(s_usn)
    if not semesters:
        st.info("No marks data available for this student.")
        return

    selected_sem = st.selectbox("Select Semester", semesters)

    rows = get_marks_for_student_sem(s_usn, selected_sem)
    if rows:
        df = pd.DataFrame(
            rows,
            columns=[
                "Subject Code",
                "Subject Name",
                "Internal Marks",
                "External Marks",
                "Total Marks",
                "Grade",
                "Result",
            ],
        )
        st.dataframe(df, use_container_width=True)

        # Semester stats
        totals = df["Total Marks"]
        avg_total = totals.mean()
        sgpa = round(avg_total / 10, 2)  # fake SGPA
        sem_result = "FAIL" if "FAIL" in df["Result"].values else "PASS"

        st.markdown("### 📊 Semester Summary")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Average Marks", f"{avg_total:.2f}")
        with col2:
            st.metric("SGPA (approx)", f"{sgpa:.2f}")
        with col3:
            if sem_result == "PASS":
                st.success("Semester Result: PASS")
            else:
                st.error("Semester Result: FAIL")
    else:
        st.info("No marks found for the selected semester.")

    st.markdown("---")

    # Overall performance
    st.subheader("🏆 Overall Performance")
    cgpa, overall_result = get_overall_stats(s_usn)
    if cgpa is None:
        st.info("No overall data available.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            st.metric("CGPA (approx)", f"{cgpa:.2f}")
        with col2:
            if overall_result == "PASS":
                st.success("Overall Status: PASS")
            else:
                st.error("Overall Status: FAIL")


# ---------- MAIN APP ----------

def main():
    st.set_page_config(page_title="Student Portal", page_icon="🎓", layout="wide")

    # Initialize database (create & seed if needed)
    init_db()

    if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
        show_login()
    else:
        show_dashboard()


if __name__ == "__main__":
    main()
