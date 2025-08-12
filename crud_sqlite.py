
#*Імпорт бібліотек.
import sqlite3
from typing import Optional, List, Dict, Tuple

#База даних для автоматичного підключення.
CURRENT_DB_PATH = "app.db"
#Деф вибору бази даних.
def set_db_path (path: str) -> None:
    global CURRENT_DB_PATH
    CURRENT_DB_PATH = path
#Деф встановлення зєднання з бд.
def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect (CURRENT_DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute ("PRAGMA foreign_keys = ON")
    return conn
#Деф ініціалізації бд за замовчуванням.
def init_db() -> None:
    with get_conn() as conn:
        conn.executescript ("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER CHECK(age >= 0),
            major TEXT
        );
        CREATE TABLE IF NOT EXISTS courses (
            course_id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_name TEXT NOT NULL,
            instructor TEXT
        );
        CREATE TABLE IF NOT EXISTS enrollments (
            student_id INTEGER NOT NULL,
            course_id INTEGER NOT NULL,
            PRIMARY KEY (student_id, course_id),
            FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE,
            FOREIGN KEY (course_id) REFERENCES courses(course_id) ON DELETE CASCADE
        );
        """)

#* ---------- Студенти ----------.
#Деф створення студента.
def create_student (name: str, age: int, major: Optional [str] = None) -> int:
    with get_conn() as conn:
        cur = conn.execute (
            "INSERT INTO students (name, age, major) VALUES (?, ?, ?)",
            (name, age, major)
        )
        return cur.lastrowid
#Деф отримання всіх студентів.
def list_students() -> List [Dict]:
    with get_conn() as conn:
        rows = conn.execute ("SELECT * FROM students ORDER BY id").fetchall()
        return [dict (r) for r in rows]
#Деф вибору студента.
def get_student (student_id: int) -> Optional [Dict]:
    with get_conn() as conn:
        row = conn.execute ("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
        return dict (row) if row else None
#Деф оновлення данних студента.
def update_student (student_id: int, name: Optional [str] = None, age: Optional [int] = None, major: Optional [str] = None) -> bool:
    fields, params = [], []
    if name is not None:
        fields.append ("name = ?"); params.append (name)
    if age is not None:
        fields.append ("age = ?"); params.append (age)
    if major is not None:
        fields.append ("major = ?"); params.append (major)
    if not fields:
        return False
    params.append (student_id)
    with get_conn() as conn:
        cur = conn.execute (f"UPDATE students SET {', '.join (fields)} WHERE id = ?", params)
        return cur.rowcount > 0
#Деф видадення студента.
def delete_student (student_id: int) -> bool:
    with get_conn() as conn:
        cur = conn.execute ("DELETE FROM students WHERE id = ?", (student_id,))
        return cur.rowcount > 0

#* ---------- Курси ----------.
#Деф створення курсу.
def create_course (course_name: str, instructor: Optional [str] = None) -> int:
    with get_conn() as conn:
        cur = conn.execute (
            "INSERT INTO courses (course_name, instructor) VALUES (?, ?)",
            (course_name, instructor)
        )
        return cur.lastrowid
#Деф Отримання списку всіх курсів.
def list_courses() -> List [Dict]:
    with get_conn() as conn:
        rows = conn.execute ("SELECT * FROM courses ORDER BY course_id").fetchall()
        return [dict (r) for r in rows]
#Деф вибору курсу.
def get_course (course_id: int) -> Optional [Dict]:
    with get_conn() as conn:
        row = conn.execute ("SELECT * FROM courses WHERE course_id = ?", (course_id,)).fetchone()
        return dict (row) if row else None
#Деф оновлення курсу.
def update_course (course_id: int, course_name: Optional [str] = None, instructor: Optional [str] = None) -> bool:
    fields, params = [], []
    if course_name is not None:
        fields.append ("course_name = ?"); params.append (course_name)
    if instructor is not None:
        fields.append ("instructor = ?"); params.append (instructor)
    if not fields:
        return False
    params.append (course_id)
    with get_conn() as conn:
        cur = conn.execute (f"UPDATE courses SET {', '.join (fields)} WHERE course_id = ?", params)
        return cur.rowcount > 0
#Деф видалення курсу.
def delete_course (course_id: int) -> bool:
    with get_conn() as conn:
        cur = conn.execute ("DELETE FROM courses WHERE course_id = ?", (course_id,))
        return cur.rowcount > 0

#* ---------- Встановлення звязку ----------.
#Деф встановлення звязку студента з курсом.
def enroll_student (student_id: int, course_id: int) -> bool:
    with get_conn() as conn:
        try:
            conn.execute (
                "INSERT INTO enrollments (student_id, course_id) VALUES (?, ?)",
                (student_id, course_id)
            )
            return True
        except sqlite3.IntegrityError:
            return False
#Деф розєднання студента від курсу.
def unenroll_student (student_id: int, course_id: int) -> bool:
    with get_conn() as conn:
        cur = conn.execute (
            "DELETE FROM enrollments WHERE student_id = ? AND course_id = ?",
            (student_id, course_id)
        )
        return cur.rowcount > 0
#Деф отримання студенів по курсу.
def list_students_by_course (course_id: int) -> List [Dict]:
    with get_conn() as conn:
        rows = conn.execute ("""
            SELECT s.*
            FROM students s
            JOIN enrollments e ON e.student_id = s.id
            WHERE e.course_id = ?
            ORDER BY s.id
        """, (course_id,)).fetchall()
        return [dict (r) for r in rows]
#!Деф отримання курсу за студентом.
def list_courses_by_student (student_id: int) -> List [Dict]:
    with get_conn() as conn:
        rows = conn.execute ("""
            SELECT c.*
            FROM courses c
            JOIN enrollments e ON e.course_id = c.course_id
            WHERE e.student_id = ?
            ORDER BY c.course_id
        """, (student_id,)).fetchall()
        return [dict (r) for r in rows]
