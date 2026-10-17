"""Q3: Import student/registration CSV files into MySQL and query a course.
Requires: pip install mysql-connector-python
CSV headers: students: student_id,name,spi; registrations: student_id,course_id
"""
import csv
import getpass
import sys
import mysql.connector
from mysql.connector import Error

SCHEMA = """
CREATE TABLE IF NOT EXISTS Student (
 student_id VARCHAR(64) PRIMARY KEY, name VARCHAR(255) NOT NULL,
 spi DECIMAL(4,2) NOT NULL, CHECK (spi >= 0 AND spi <= 10)
) ENGINE=InnoDB
"""
REG_SCHEMA = """
CREATE TABLE IF NOT EXISTS CourseRegistration (
 student_id VARCHAR(64) NOT NULL, course_id VARCHAR(64) NOT NULL,
 PRIMARY KEY (student_id, course_id), INDEX idx_course (course_id),
 FOREIGN KEY (student_id) REFERENCES Student(student_id)
) ENGINE=InnoDB
"""
def rows(path, required):
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames or not set(required).issubset(reader.fieldnames): raise ValueError(f"{path} must have headers: {', '.join(required)}")
        for line, row in enumerate(reader, 2):
            try:
                if "spi" in required:
                    spi = float(row["spi"])
                    if not 0 <= spi <= 10: raise ValueError("SPI outside 0..10")
                    yield (row["student_id"].strip(), row["name"].strip(), spi)
                else: yield (row["student_id"].strip(), row["course_id"].strip())
            except (KeyError, ValueError) as exc: raise ValueError(f"Invalid row {line} in {path}: {exc}")
def main():
    conn = None
    try:
        host = input("MySQL host [localhost]: ").strip() or "localhost"
        user = input("MySQL user: ").strip()
        password = getpass.getpass("MySQL password: ")
        database = input("Database name: ").strip()
        student_csv = input("Student CSV path: ").strip()
        registration_csv = input("Registration CSV path: ").strip()
        course_id = input("Course ID: ").strip()
        threshold = float(input("SPI threshold (0..10): "))
        if not user or not database or not 0 <= threshold <= 10: raise ValueError("User/database are required and threshold must be in 0..10.")
        conn = mysql.connector.connect(host=host, user=user, password=password, database=database)
        cur = conn.cursor()
        cur.execute(SCHEMA); cur.execute(REG_SCHEMA)
        cur.executemany("INSERT INTO Student(student_id,name,spi) VALUES(%s,%s,%s) ON DUPLICATE KEY UPDATE name=VALUES(name),spi=VALUES(spi)", rows(student_csv, ("student_id","name","spi")))
        cur.executemany("INSERT IGNORE INTO CourseRegistration(student_id,course_id) VALUES(%s,%s)", rows(registration_csv, ("student_id","course_id")))
        conn.commit()
        cur.execute("SELECT s.student_id,s.name,s.spi,r.course_id FROM Student s JOIN CourseRegistration r ON r.student_id=s.student_id WHERE r.course_id=%s AND s.spi>%s ORDER BY s.spi DESC,s.student_id ASC", (course_id, threshold))
        for rec in cur: print(*rec)
        cur.close()
    except (Error, OSError, ValueError) as exc:
        if conn: conn.rollback()
        print(f"Error: {exc}", file=sys.stderr); raise SystemExit(1)
    finally:
        if conn and conn.is_connected(): conn.close()
if __name__ == "__main__": main()
