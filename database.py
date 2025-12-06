import sqlite3
import random
import os

DB_NAME = "student_portal.db"

# Delete old DB if exists (fresh start)
if os.path.exists(DB_NAME):
    os.remove(DB_NAME)

conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()

# ---------- CREATE TABLES ----------

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
);
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
    result TEXT,
    FOREIGN KEY(usn) REFERENCES students(usn)
);
""")

# ---------- INSERT 30 SAMPLE STUDENTS ----------

branches = ["CSE", "ECE", "ME", "EEE", "CIVIL"]
sections = ["A", "B"]

for i in range(1, 31):
    usn = f"USN{i:03d}"
    name = f"Student {i}"
    branch = random.choice(branches)
    semester = random.randint(1, 8)
    section = random.choice(sections)
    email = f"student{i}@college.edu"
    phone = f"9{random.randint(100000000, 999999999)}"
    password = "password"
    photo_url = ""

    cur.execute("""
    INSERT INTO students (usn, name, branch, semester, section, email, phone, password, photo_url)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (usn, name, branch, semester, section, email, phone, password, photo_url))

    # ---------- INSERT SEM 1 & 2 MARKS ----------
    for sem in [1, 2]:
        subjects = [
            ("MAT", "Mathematics"),
            ("PHY", "Physics"),
            ("CS", "Computer Science"),
            ("ELE", "Electronics"),
            ("ENG", "English"),
        ]

        for code, sub_name in subjects:
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

            cur.execute("""
            INSERT INTO marks (usn, semester, subject_code, subject_name, internal, external, total, grade, result)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (usn, sem, code, f"{sub_name} {sem}", internal, external, total, grade, result))

conn.commit()
conn.close()

print("✅ Database created successfully: student_portal.db")
