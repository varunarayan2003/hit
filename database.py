import sqlite3
import random
import os

DB_NAME = "student_portal.db"

# ------------------------------
# (OPTIONAL) DELETE OLD DATABASE
# ------------------------------
# ⚠️ If you run this script multiple times, it will always recreate the DB
#    and delete all previous data.
#    If you DON'T want that, comment out the next 3 lines after first run.

if os.path.exists(DB_NAME):
    os.remove(DB_NAME)
    print("Old database deleted. Creating a fresh one...")

# ------------------------------
# CONNECT TO DATABASE
# ------------------------------
conn = sqlite3.connect(DB_NAME)
cur = conn.cursor()

# ------------------------------
# CREATE TABLES
# ------------------------------
cur.execute("""
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
    FOREIGN KEY(usn) REFERENCES students(usn)
);
""")

print("✅ Tables created successfully")

# ------------------------------
# HELPER: GRADE CALCULATION
# ------------------------------
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

# ------------------------------
# INSERT 30 SAMPLE STUDENTS
# ------------------------------
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

    # Only sample marks for SEM 1 & 2 for these dummy students
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
            grade = calculate_grade(total)
            result = "PASS" if total >= 50 else "FAIL"

            cur.execute("""
            INSERT INTO marks (usn, semester, subject_code, subject_name, internal, external, total, grade, result)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (usn, sem, code, f"{sub_name} {sem}", internal, external, total, grade, result))

print("✅ 30 sample students + marks inserted")

# ------------------------------
# INSERT REAL STUDENT: KIM0045
# ------------------------------
cur.execute("""
INSERT OR IGNORE INTO students
(usn, name, branch, semester, section, email, phone, password, photo_url)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    "KIM0045",
    "JANARDHANA N",
    "CSE",          # you can change branch if needed
    6,              # final semester
    "A",            # section assumption
    "janardhana@example.com",
    "9876543210",
    "password",
    ""
))

print("✅ Real student KIM0045 inserted/updated")

# ------------------------------
# REAL MARKS DATA FOR KIM0045
# (All values taken from your mark statements)
# ------------------------------


real_marks_data = [

    # ---------- SEM 1 ----------
    (1, "10CS-01",  "ENGINEERING MATHS -I",          18, 45),
    (1, "10CS-03",  "APPLIED SCIENCE",              20, 60),
    (1, "10CS-04",  "CNCPT OF ELE & ELECTROENGG",   20, 65),
    (1, "10CS-10P", "APPLIED SCIENCE LAB",          18, 50),
    (1, "10CS-12P", "BASIC ELECTRONICS LAB",        16, 55),
    (1, "10CS-11P", "B C S LAB",                    23, 59),

    # ---------- SEM 2 ----------
    (2, "10CS-07",  "ENGINEERING MATHS -II",        18, 50),
    (2, "10CS-08",  "COMMN SKILLS IN ENGLISH",      15, 59),
    (2, "10CS-09",  "DIGITAL & COMP FUNDMNTLS",     16, 62),
    (2, "10CS-10",  "DIGITAL ELECTRONICS LAB",      14, 55),
    (2, "10CS-11",  "BASIC WEB DESIGN LAB",         15, 60),
    (2, "1OCS-12",  "MULTIMEDIA LAB",               22, 50),

    # ---------- SEM 3 ----------
    (3, "10CS11T",  "PROGRAMMING WITH C",           15, 50),
    (3, "10CS23T",  "COMPUTER ORGANISATION",        21, 45),
    (3, "10CS43T",  "DBMS",                         18, 60),
    (3, "10CS13T",  "COMPUTER NETWORKS",            19, 52),
    (3, "10CS11P",  "PROGRAMMING WITH C LAB",       20, 50),
    (3, "10CS13P",  "N/W ADMINSTRATION LAB",        21, 54),

    # ---------- SEM 4 ----------
    (4, "10CS15T",  "DATA STRUCTURES USING C",      17, 50),
    (4, "10CS20T",  "OOP WITH JAVA",                22, 45),
    (4, "10CS90T",  "OPERATING SYSTEM",             20, 42),
    (4, "10CS43P",  "DATA STRUCTURES LAB",          19, 52),
    (4, "10CS01P",  "OOP WITH JAVA LAB",            20, 50),
    (4, "10CS03P",  "LINUX LAB",                    21, 59),

    # ---------- SEM 5 ----------
    (5, "10CS51T",  "SOFTWARE ENGINEER",            19, 55),
    (5, "10CS52T",  "WEB",                          22, 50),
    (5, "10CS53T",  "ADA",                          22, 45),
    (5, "10CS55P",  "WEB LAB",                      14, 52),
    (5, "10CS57P",  "ADA LAB",                      18, 55),
    (5, "10CS58P",  "PROJECT -I",                   21, 60),

    # ---------- SEM 6 ----------
    (6, "10CS61T",  "SOFTWARE TESTING",             18, 40),
    (6, "10CS62T",  "NETWORK SECURITY",             20, 46),
    (6, "10CS63T",  "INTERNET OF THINGS",           22, 52),
    (6, "10CS65P",  "NETWORK SECURITY LAB",         15, 58),
    (6, "10CS66P",  "IMPLANT TRAINING",             20, 55),
    (6, "10CS67P",  "PROJECT WORK -II",             21, 62),
]

# First, delete old marks for this USN (if any), to avoid duplicates
cur.execute("DELETE FROM marks WHERE usn = ?", ("KIM0045",))

for sem, code, name, internal, external in real_marks_data:
    total = internal + external
    grade = calculate_grade(total)
    result = "PASS" if total >= 40 else "FAIL"

    cur.execute("""
    INSERT INTO marks
    (usn, semester, subject_code, subject_name, internal, external, total, grade, result)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "KIM0045",
        sem,
        code,
        name,
        internal,
        external,
        total,
        grade,
        result
    ))

print("✅ Real marks for KIM0045 inserted")

# ------------------------------
# FINALIZE
# ------------------------------
conn.commit()
conn.close()

print("🎉 Done! Database created:", DB_NAME)
