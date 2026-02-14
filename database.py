import sqlite3
import random
import os

DB_NAME = "student_portal.db"

# ------------------------------
# DELETE OLD DATABASE (OPTIONAL)
# ------------------------------
if os.path.exists(DB_NAME):
    os.remove(DB_NAME)
    print("Old database deleted. Creating a fresh one.")

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
# GRADE FUNCTION
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
# INSERT REAL STUDENT
# ------------------------------
cur.execute("""
INSERT INTO students
(usn, name, branch, semester, section, email, phone, password, photo_url)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    "506CS20188",
    "KOUSHIK N",
    "CSE",
    6,
    "A",
    "koushik@example.com",
    "9876543210",
    "password",
    ""
))

print("✅ Real student KOUSHIK N inserted")

# ------------------------------
# REAL MARKS DATA (OFFICIAL)
# ------------------------------
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

print("✅ Official marks inserted successfully")

# ------------------------------
# FINALIZE
# ------------------------------
conn.commit()
conn.close()

print("🎉 Database created successfully:", DB_NAME)
