import sqlite3
import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify, g, url_for, session, redirect, flash
from functools import wraps

APP_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(APP_DIR, "attendance.db")

app = Flask(__name__)
app.secret_key = 'your_very_secret_key'

# ---------- DB Helpers ----------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db

@app.teardown_appcontext
def close_db(_):
    db = g.pop("db", None)
    if db:
        db.close()

# ---------- Database Initialization ----------
def init_db():
    db = get_db()
    db.executescript(
        """
        PRAGMA foreign_keys = ON;
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('admin', 'teacher', 'student'))
        );
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll_no TEXT UNIQUE NOT NULL, name TEXT NOT NULL, exercism_username TEXT,
            user_id INTEGER UNIQUE,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE SET NULL
        );
        CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE NOT NULL
        );
        CREATE TABLE IF NOT EXISTS homework (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_id INTEGER NOT NULL, title TEXT NOT NULL, description TEXT,
            posted_date TEXT NOT NULL, due_date TEXT NOT NULL,
            FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS homework_submissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            homework_id INTEGER NOT NULL, student_id INTEGER NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending', grade INTEGER,
            FOREIGN KEY(homework_id) REFERENCES homework(id) ON DELETE CASCADE,
            FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE,
            UNIQUE(homework_id, student_id)
        );
        CREATE TABLE IF NOT EXISTS doubts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            homework_id INTEGER NOT NULL, student_id INTEGER NOT NULL,
            question TEXT NOT NULL, answer TEXT, asked_date TEXT NOT NULL,
            FOREIGN KEY(homework_id) REFERENCES homework(id) ON DELETE CASCADE,
            FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT NOT NULL,
            subject_id INTEGER NOT NULL, student_id INTEGER NOT NULL,
            status TEXT CHECK(status IN ('Present','Absent Informed','Absent Uninformed')) NOT NULL,
            UNIQUE(date, subject_id, student_id),
            FOREIGN KEY(subject_id) REFERENCES subjects(id) ON DELETE CASCADE,
            FOREIGN KEY(student_id) REFERENCES students(id) ON DELETE CASCADE
        );
        """
    )
    try:
        cur = db.execute("PRAGMA table_info(students)")
        cols = [column[1] for column in cur.fetchall()]
        if 'exercism_username' not in cols:
            db.execute("ALTER TABLE students ADD COLUMN exercism_username TEXT")
        if 'user_id' not in cols:
             db.execute("ALTER TABLE students ADD COLUMN user_id INTEGER UNIQUE REFERENCES users(id) ON DELETE SET NULL")

    except sqlite3.OperationalError:
        pass

    cur = db.execute("SELECT COUNT(*) c FROM users")
    if cur.fetchone()['c'] == 0:
        db.execute("INSERT INTO users (username, password, role) VALUES (?,?,?)",('admin','admin','admin'))

    cur = db.execute("SELECT COUNT(*) c FROM subjects")
    if cur.fetchone()["c"] == 0:
        subjects = [ "Software Engineering","Mobile Applications","Data Structure","Mathematics", "Information Security","Frontend Development","Basic Indian Language", "Information Security lab","Frontend Development lab","Mobile Applications lab", "Data Structure lab","Integral Yoga" ]
        db.executemany("INSERT INTO subjects(name) VALUES(?)", [(s,) for s in subjects])

    cur = db.execute("SELECT COUNT(*) c FROM students")
    if cur.fetchone()["c"] == 0:
        students = [
            ("24820001", "Aravindh", "devaravindh-ml-exercism"),
            ("24820002", "Aswin", "aswinas04-exercism"),
            ("24820003", "Bavana", "bhavana2912-exercism"),
            ("24820004", "Gokul", "gokulramesh502-exercism"),
            ("24820005", "Hariharan", "hariharan-exercism"),
            ("24820006", "Meenatchi", "meenatchi-exercism"),
            ("24820007", "Siva Bharathi", "Sivabharathi-Ramesh-exercism"),
            ("24820008", "Visal Stephen Raj", "Visalstephenraj-exercism"),
        ]
        db.executemany("INSERT INTO students(roll_no, name, exercism_username) VALUES(?, ?, ?)", students)
    db.commit()
    print("Database initialized successfully.")


# ---------- Auth Decorators ----------
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session.get('role') != role:
                flash("You do not have permission to access this page.", "danger")
                return redirect(url_for('home'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ---------- Auth Routes ----------
@app.route("/login", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username = ? AND role = ?", (username, role)).fetchone()
        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            return redirect(url_for('home'))
        else:
            flash("Invalid credentials or role.", "danger")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))


# ---------- Main Pages ----------
@app.route("/")
@login_required
def home():
    if session['role'] == 'student':
        return redirect(url_for('student_dashboard'))
    elif session['role'] == 'teacher':
        return redirect(url_for('teacher_dashboard'))
    return render_template("new_home.html", page="home")

@app.route("/student/dashboard")
@login_required
@role_required('student')
def student_dashboard():
    db = get_db()
    user_id = session['user_id']
    student = db.execute("SELECT id, exercism_username FROM students WHERE user_id = ?", (user_id,)).fetchone()
    exercism_username = student['exercism_username'] if student else None
    return render_template("student_dashboard.html", page="student_dashboard", exercism_username=exercism_username)

@app.route("/teacher/dashboard")
@login_required
@role_required('teacher')
def teacher_dashboard():
    return render_template("teacher_dashboard.html", page="teacher_dashboard")

@app.route("/attendance")
@login_required
def attendance_home():
    return render_template("attendance_home.html", page="attendance_home")

@app.route("/store")
@login_required
def store():
    if session['role'] == 'student':
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('home'))
    return render_template("store.html", page="store")

@app.route("/student/attendance")
@login_required
@role_required('student')
def student_attendance_view():
    return render_template("student_attendance.html", page="student_attendance")

@app.route("/student/doubts")
@login_required
@role_required('student')
def student_doubts():
    return render_template("student_doubts.html", page="student_doubts")

@app.route("/teacher/doubts")
@login_required
def teacher_doubts_list():
    if session['role'] == 'student':
        return redirect(url_for('student_doubts'))
    return render_template("teacher_doubts.html", page="teacher_doubts")

@app.route("/teacher/analytics")
@login_required
def teacher_analytics():
    if session['role'] == 'student':
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('home'))
    return render_template("teacher_analytics.html", page="teacher_analytics")

@app.route("/view")
@login_required
def view():
    return render_template("view.html", page="view")

@app.route("/individual")
@login_required
def individual():
    return render_template("individual.html", page="individual")

@app.route("/homework")
@login_required
def homework_home():
    return render_template("homework_home.html", page="homework_home")

@app.route("/homework/manage")
@login_required
def manage_homework():
    if session['role'] == 'student':
        return redirect(url_for('homework_status'))
    db = get_db()
    subject_filter = request.args.get("subject_id", type=int)
    date_filter = request.args.get("date", type=str)
    base_query = """
        SELECT h.id, h.title, h.description, h.posted_date, h.due_date, s.name as subject, s.id as subject_id
        FROM homework h JOIN subjects s ON h.subject_id = s.id
    """
    conditions = []; params = []
    if subject_filter:
        conditions.append("h.subject_id = ?"); params.append(subject_filter)
    if date_filter:
        dmy_date = datetime.strptime(date_filter, "%Y-%m-%d").strftime("%d-%m-%Y")
        conditions.append("h.posted_date = ?"); params.append(dmy_date)
    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)
    base_query += " ORDER BY substr(h.posted_date,7,4)||'-'||substr(h.posted_date,4,2)||'-'||substr(h.posted_date,1,2) DESC"
    
    homeworks = db.execute(base_query, params).fetchall()
    students = db.execute("SELECT id, name FROM students ORDER BY name").fetchall()
    submissions = {}
    if homeworks:
        hw_ids = [h['id'] for h in homeworks]
        submission_rows = db.execute(f"SELECT homework_id, student_id, grade FROM homework_submissions WHERE homework_id IN ({','.join(['?']*len(hw_ids))})", hw_ids).fetchall()
        for sub in submission_rows:
            if sub['homework_id'] not in submissions: submissions[sub['homework_id']] = {}
            submissions[sub['homework_id']][sub['student_id']] = sub['grade']

    return render_template("manage_homework.html", page="manage_homework", homeworks=homeworks, students=students, submissions=submissions)

@app.route("/homework/status")
@login_required
def homework_status():
    db = get_db()
    student_id = None
    if session['role'] == 'student':
        user_id = session['user_id']
        student = db.execute("SELECT id FROM students WHERE user_id = ?", (user_id,)).fetchone()
        if student:
            student_id = student['id']
    else:
        first_student = db.execute("SELECT id FROM students LIMIT 1").fetchone()
        if first_student:
            student_id = first_student['id']
            
    if not student_id:
        return render_template("homework_status.html", page="homework_status", homeworks=[])

    homeworks = db.execute("""
        SELECT h.id, h.title, h.description, h.due_date, s.name as subject,
               COALESCE(hs.status, 'Pending') as student_status
        FROM homework h JOIN subjects s ON h.subject_id = s.id
        LEFT JOIN homework_submissions hs ON hs.homework_id = h.id AND hs.student_id = ?
        ORDER BY substr(h.due_date,7,4)||'-'||substr(h.due_date,4,2)||'-'||substr(h.due_date,1,2) ASC
    """, (student_id,)).fetchall()
    return render_template("homework_status.html", page="homework_status", homeworks=homeworks)
    
@app.route("/homework/doubts/<int:homework_id>")
@login_required
def homework_doubts(homework_id):
    db = get_db()
    homework = db.execute("SELECT id, title FROM homework WHERE id = ?", (homework_id,)).fetchone()
    students = db.execute("SELECT id, name FROM students ORDER BY name").fetchall()
    doubts = db.execute("SELECT d.id, d.question, d.answer, s.name as student_name, d.asked_date FROM doubts d JOIN students s ON d.student_id = s.id WHERE d.homework_id = ? ORDER BY d.asked_date DESC", (homework_id,)).fetchall()
    return render_template("homework_doubts.html", page="homework_doubts", homework=homework, doubts=doubts, students=students)

@app.route("/homework/calendar")
@login_required
def homework_calendar():
    return render_template("calendar.html", page="homework_calendar")

@app.route("/exercism")
@login_required
def exercism():
    db = get_db()
    students = db.execute("SELECT name, exercism_username FROM students WHERE exercism_username IS NOT NULL").fetchall()
    return render_template("exercism.html", page="exercism", students=students)

@app.route('/admin/manage_users')
@login_required
@role_required('admin')
def manage_users():
    db = get_db()
    users = db.execute("SELECT u.id, u.username, u.role, s.name as student_name FROM users u LEFT JOIN students s ON s.user_id = u.id ORDER BY u.role, u.username").fetchall()
    students_without_users = db.execute("SELECT id, name FROM students WHERE user_id IS NULL ORDER BY name").fetchall()
    return render_template('manage_users.html', users=users, students_without_users=students_without_users, page='manage_users')

# ---------- APIs ----------
@app.route("/api/subjects")
@login_required
def api_subjects():
    db = get_db()
    rows = db.execute("SELECT id, name FROM subjects ORDER BY name").fetchall()
    return jsonify([dict(row) for row in rows])

@app.route("/api/students")
@login_required
def api_students():
    db = get_db()
    rows = db.execute("SELECT id, roll_no, name FROM students ORDER BY name").fetchall()
    return jsonify([dict(row) for row in rows])

@app.route("/api/save_attendance", methods=["POST"])
@login_required
def api_save_attendance():
    # UPDATED: This now blocks students
    if session['role'] == 'student':
        return jsonify({"ok": False, "error": "Unauthorized"}), 403

    data = request.get_json(force=True)
    date = data.get("date")
    subject_id = data.get("subject_id")
    marks = data.get("marks", [])
    try: datetime.strptime(date, "%d-%m-%Y")
    except Exception: return jsonify({"ok": False, "error": "Invalid date format; use dd-mm-yyyy"}), 400
    if not subject_id or not isinstance(marks, list) or len(marks) == 0: return jsonify({"ok": False, "error": "Missing subject or marks"}), 400
    db = get_db()
    s = db.execute("SELECT id FROM subjects WHERE id=?", (subject_id,)).fetchone()
    if not s: return jsonify({"ok": False, "error": "Subject not found"}), 404
    for m in marks:
        sid = m.get("student_id")
        status = m.get("status")
        if status not in ("Present", "Absent Informed", "Absent Uninformed"): return jsonify({"ok": False, "error": "Invalid status"}), 400
        st = db.execute("SELECT id FROM students WHERE id=?", (sid,)).fetchone()
        if not st: return jsonify({"ok": False, "error": f"Student {sid} not found"}), 404
        db.execute("INSERT INTO attendance(date, subject_id, student_id, status) VALUES(?,?,?,?) ON CONFLICT(date, subject_id, student_id) DO UPDATE SET status=excluded.status", (date, subject_id, sid, status))
    db.commit()
    return jsonify({"ok": True})

@app.route("/api/get_attendance_for_store")
@login_required
def api_get_attendance_for_store():
    subject_id = request.args.get("subject_id", type=int)
    date = request.args.get("date", type=str)
    try: datetime.strptime(date, "%d-%m-%Y")
    except Exception: return jsonify({"ok": False, "error": "Invalid date format; use dd-mm-yyyy"}), 400
    db = get_db()
    rows = db.execute("SELECT st.id as student_id, COALESCE(a.status, 'none') AS status FROM students st LEFT JOIN attendance a ON a.student_id = st.id AND a.subject_id = ? AND a.date = ?", (subject_id, date)).fetchall()
    return jsonify({"ok": True, "records": [dict(r) for r in rows]})

@app.route("/api/get_attendance")
@login_required
def api_get_attendance():
    db = get_db()
    subject_id = request.args.get("subject_id", type=int)
    filter_type = request.args.get("filter_type", "day")
    if not subject_id: return jsonify({"ok": False, "error": "Subject ID is required"}), 400
    if filter_type == "day":
        date = request.args.get("date", type=str)
        if not date: return jsonify({"ok": False, "error": "Date is required for day view"}), 400
        try: datetime.strptime(date, "%d-%m-%Y")
        except (ValueError, TypeError): return jsonify({"ok": False, "error": "Invalid date format"}), 400
        rows = db.execute("SELECT st.roll_no, st.name, COALESCE(a.status,'Absent Uninformed') AS status FROM students st LEFT JOIN attendance a ON a.student_id = st.id AND a.subject_id = ? AND a.date = ? ORDER BY st.name", (subject_id, date)).fetchall()
        return jsonify({"ok": True, "records": [dict(r) for r in rows]})
    else:
        base_query = "SELECT a.date, st.roll_no, st.name, a.status FROM attendance a JOIN students st ON a.student_id = st.id WHERE a.subject_id = ?"
        params = [subject_id]
        if filter_type == "year":
            year = request.args.get("year", type=str)
            if not year: return jsonify({"ok": False, "error": "Year is required"}), 400
            base_query += " AND substr(a.date, 7, 4) = ?"
            params.append(year)
        elif filter_type == "month":
            year = request.args.get("year", type=str)
            month = request.args.get("month", type=str)
            if not year or not month: return jsonify({"ok": False, "error": "Year and month are required"}), 400
            base_query += " AND substr(a.date, 7, 4) = ? AND substr(a.date, 4, 2) = ?"
            params.extend([year, month.zfill(2)])
        base_query += " ORDER BY substr(a.date,7,4), substr(a.date,4,2), substr(a.date,1,2), st.name"
        rows = db.execute(base_query, params).fetchall()
        return jsonify({"ok": True, "records": [dict(r) for r in rows]})

@app.route("/api/student_report")
@login_required
def api_student_report():
    q = (request.args.get("query") or "").strip()
    subject_id = request.args.get("subject_id")
    date_type = request.args.get("dateType")
    year = request.args.get("year")
    month = request.args.get("month")
    date = request.args.get("date")
    db = get_db()
    stu = db.execute("SELECT * FROM students WHERE roll_no LIKE ? OR name LIKE ? ORDER BY name LIMIT 1", (f"%{q}%", f"%{q}%")).fetchone()
    if not stu: return jsonify({"ok": True, "student": None, "rows": []})
    conditions = ["a.student_id = ?"]; params = [stu["id"]]
    if subject_id: conditions.append("a.subject_id = ?"); params.append(subject_id)
    if date_type == "year" and year: conditions.append("substr(a.date,7,4) = ?"); params.append(year)
    if date_type == "month" and month and year:
        conditions.append("substr(a.date,4,2) = ? AND substr(a.date,7,4) = ?"); params.extend([month.zfill(2), year])
    if date_type == "date" and date:
        try:
            dmy = datetime.strptime(date, "%Y-%m-%d").strftime("%d-%m-%Y")
            conditions.append("a.date = ?"); params.append(dmy)
        except (ValueError, TypeError): return jsonify({"ok": False, "error": "Invalid date format"}), 400
    query = f"SELECT a.date, s.name AS subject, a.status FROM attendance a JOIN subjects s ON s.id = a.subject_id WHERE {' AND '.join(conditions)} ORDER BY substr(a.date,7,4)||'-'||substr(a.date,4,2)||'-'||substr(a.date,1,2) ASC, s.name ASC"
    rows = db.execute(query, params).fetchall()
    return jsonify({"ok": True, "student": {"id": stu["id"], "roll_no": stu["roll_no"], "name": stu["name"]}, "rows": [dict(r) for r in rows]})

@app.route("/api/homework", methods=["POST"])
@login_required
def api_add_homework():
    if session['role'] == 'student':
        return jsonify({"ok": False, "error": "Unauthorized"}), 403
    data = request.get_json()
    posted_date = datetime.now().strftime("%d-%m-%Y")
    due_date = datetime.strptime(data['due_date'], "%Y-%m-%d").strftime("%d-%m-%Y")
    db = get_db()
    cursor = db.execute("INSERT INTO homework (subject_id, title, description, posted_date, due_date) VALUES (?, ?, ?, ?, ?)", (data['subject_id'], data['title'], data.get('description', ''), posted_date, due_date))
    db.commit()
    return jsonify({"ok": True, "new_id": cursor.lastrowid, "posted_date": posted_date})

@app.route("/api/homework/<int:homework_id>", methods=["POST"])
@login_required
def api_update_homework(homework_id):
    if session['role'] == 'student':
        return jsonify({"ok": False, "error": "Unauthorized"}), 403
    data = request.get_json(force=True)
    due_date = datetime.strptime(data.get("due_date"), "%Y-%m-%d").strftime("%d-%m-%Y")
    db = get_db()
    db.execute("UPDATE homework SET subject_id = ?, title = ?, description = ?, due_date = ? WHERE id = ?", (data.get("subject_id"), data.get("title"), data.get("description"), due_date, homework_id))
    db.commit()
    return jsonify({"ok": True})

@app.route("/api/homework/<int:homework_id>", methods=["DELETE"])
@login_required
def api_delete_homework(homework_id):
    if session['role'] == 'student':
        return jsonify({"ok": False, "error": "Unauthorized"}), 403
    db = get_db()
    db.execute("DELETE FROM homework WHERE id = ?", (homework_id,))
    db.commit()
    return jsonify({"ok": True})

@app.route("/api/homework/grade", methods=["POST"])
@login_required
def api_grade_homework():
    if session['role'] == 'student':
        return jsonify({"ok": False, "error": "Unauthorized"}), 403
    data = request.get_json()
    db = get_db()
    db.execute("INSERT INTO homework_submissions (homework_id, student_id, grade, status) VALUES (?, ?, ?, 'Graded') ON CONFLICT(homework_id, student_id) DO UPDATE SET grade = excluded.grade, status = 'Graded'",(data['homework_id'], data['student_id'], data.get('grade')))
    db.commit()
    return jsonify({"ok": True})

@app.route("/api/doubts/ask", methods=["POST"])
@login_required
def api_ask_doubt():
    data = request.get_json()
    student_id = data.get('student_id')
    if not student_id: return jsonify({"ok": False, "message": "Please select a student."}), 400
    asked_date = datetime.now().strftime("%d-%m-%Y %H:%M")
    db = get_db()
    db.execute("INSERT INTO doubts (homework_id, student_id, question, asked_date) VALUES (?, ?, ?, ?)",(data['homework_id'], student_id, data['question'], asked_date))
    db.commit()
    return jsonify({"ok": True, "message": "Doubt posted!"})

@app.route("/api/doubts/answer", methods=["POST"])
@login_required
def api_answer_doubt():
    if session['role'] == 'student':
        return jsonify({"ok": False, "error": "Unauthorized"}), 403
    data = request.get_json()
    db = get_db()
    db.execute("UPDATE doubts SET answer = ? WHERE id = ?",(data['answer'], data['doubt_id']))
    db.commit()
    return jsonify({"ok": True, "message": "Answer posted!"})

@app.route("/api/doubts/<int:doubt_id>", methods=["POST"])
@login_required
def api_update_doubt(doubt_id):
    data = request.get_json()
    question_text = data.get("question")
    if not question_text: return jsonify({"ok": False, "message": "Question text cannot be empty."}), 400
    db = get_db()
    db.execute("UPDATE doubts SET question = ? WHERE id = ?", (question_text, doubt_id))
    db.commit()
    return jsonify({"ok": True})

@app.route("/api/doubts/<int:doubt_id>", methods=["DELETE"])
@login_required
def api_delete_doubt(doubt_id):
    db = get_db()
    db.execute("DELETE FROM doubts WHERE id = ?", (doubt_id,))
    db.commit()
    return jsonify({"ok": True})

@app.route("/api/homework/events")
@login_required
def api_homework_events():
    db = get_db()
    homeworks = db.execute("SELECT id, title, due_date FROM homework").fetchall()
    events = []
    for hw in homeworks:
        try:
            d, m, y = hw['due_date'].split('-')
            start_date = f"{y}-{m}-{d}"
            events.append({'title': hw['title'],'start': start_date,'url': url_for('homework_doubts', homework_id=hw['id']),'color': '#b58900'})
        except (ValueError, IndexError): continue
    return jsonify(events)

@app.route('/api/users', methods=['POST'])
@login_required
@role_required('admin')
def add_user():
    data = request.get_json()
    db = get_db()
    try:
        cursor = db.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (data['username'], data['password'], data['role']))
        new_user_id = cursor.lastrowid
        if data.get('role') == 'student' and data.get('student_id'):
            db.execute("UPDATE students SET user_id = ? WHERE id = ?", (new_user_id, data['student_id']))
        db.commit()
        return jsonify({"ok": True})
    except sqlite3.IntegrityError:
        return jsonify({"ok": False, "error": "Username already exists."}), 409

@app.route('/api/users/<int:user_id>', methods=['DELETE'])
@login_required
@role_required('admin')
def delete_user(user_id):
    db = get_db()
    db.execute("DELETE FROM users WHERE id = ?", (user_id,))
    db.commit()
    return jsonify({"ok": True})

# Student API Routes
@app.route("/api/student/dashboard_stats")
@login_required
@role_required('student')
def api_student_dashboard_stats():
    db = get_db()
    user_id = session['user_id']
    student = db.execute("SELECT id FROM students WHERE user_id = ?", (user_id,)).fetchone()
    if not student:
        return jsonify({"ok": False, "error": "Student profile not found"}), 404
    student_id = student['id']

    homework_stats = db.execute("""
        SELECT
            SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN status = 'Submitted' THEN 1 ELSE 0 END) as submitted,
            SUM(CASE WHEN status = 'Graded' THEN 1 ELSE 0 END) as graded
        FROM homework_submissions WHERE student_id = ?
    """, (student_id,)).fetchone()

    attendance_stats = db.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present
        FROM attendance WHERE student_id = ?
    """, (student_id,)).fetchone()

    doubts_stats = db.execute("""
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN answer IS NOT NULL AND answer != '' THEN 1 ELSE 0 END) as answered
        FROM doubts WHERE student_id = ?
    """, (student_id,)).fetchone()

    attendance_percentage = 0
    if attendance_stats['total'] > 0:
        attendance_percentage = round((attendance_stats['present'] / attendance_stats['total']) * 100, 1)

    return jsonify({
        "ok": True,
        "homework": {
            "pending": homework_stats['pending'] or 0,
            "submitted": homework_stats['submitted'] or 0,
            "graded": homework_stats['graded'] or 0
        },
        "attendance": {
            "total": attendance_stats['total'] or 0,
            "present": attendance_stats['present'] or 0,
            "percentage": attendance_percentage
        },
        "doubts": {
            "total": doubts_stats['total'] or 0,
            "answered": doubts_stats['answered'] or 0,
            "pending": (doubts_stats['total'] or 0) - (doubts_stats['answered'] or 0)
        }
    })

@app.route("/api/student/attendance")
@login_required
@role_required('student')
def api_student_attendance():
    db = get_db()
    user_id = session['user_id']
    student = db.execute("SELECT id FROM students WHERE user_id = ?", (user_id,)).fetchone()
    if not student:
        return jsonify({"ok": False, "error": "Student profile not found"}), 404
    student_id = student['id']

    subject_id = request.args.get('subject_id', type=int)
    month = request.args.get('month', type=str)
    year = request.args.get('year', type=str)

    query = "SELECT a.date, s.name as subject, a.status FROM attendance a JOIN subjects s ON a.subject_id = s.id WHERE a.student_id = ?"
    params = [student_id]

    if subject_id:
        query += " AND a.subject_id = ?"
        params.append(subject_id)
    if month and year:
        query += " AND substr(a.date, 4, 2) = ? AND substr(a.date, 7, 4) = ?"
        params.extend([month.zfill(2), year])
    elif year:
        query += " AND substr(a.date, 7, 4) = ?"
        params.append(year)

    query += " ORDER BY substr(a.date,7,4)||'-'||substr(a.date,4,2)||'-'||substr(a.date,1,2) DESC"
    records = db.execute(query, params).fetchall()

    summary_query = """
        SELECT
            COUNT(*) as total,
            SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present,
            SUM(CASE WHEN status = 'Absent Informed' THEN 1 ELSE 0 END) as absent_informed,
            SUM(CASE WHEN status = 'Absent Uninformed' THEN 1 ELSE 0 END) as absent_uninformed
        FROM attendance WHERE student_id = ?
    """
    summary_params = [student_id]

    if subject_id:
        summary_query += " AND subject_id = ?"
        summary_params.append(subject_id)
    if month and year:
        summary_query += " AND substr(date, 4, 2) = ? AND substr(date, 7, 4) = ?"
        summary_params.extend([month.zfill(2), year])
    elif year:
        summary_query += " AND substr(date, 7, 4) = ?"
        summary_params.append(year)

    summary = db.execute(summary_query, summary_params).fetchone()
    percentage = 0
    if summary['total'] > 0:
        percentage = round((summary['present'] / summary['total']) * 100, 1)

    return jsonify({
        "ok": True,
        "records": [dict(r) for r in records],
        "summary": {
            "total": summary['total'],
            "present": summary['present'],
            "absent_informed": summary['absent_informed'],
            "absent_uninformed": summary['absent_uninformed'],
            "percentage": percentage
        }
    })

@app.route("/api/student/doubts")
@login_required
@role_required('student')
def api_student_doubts():
    db = get_db()
    user_id = session['user_id']
    student = db.execute("SELECT id FROM students WHERE user_id = ?", (user_id,)).fetchone()
    if not student:
        return jsonify({"ok": False, "error": "Student profile not found"}), 404
    student_id = student['id']

    homework_id = request.args.get('homework_id', type=int)
    query = "SELECT d.id, d.question, d.answer, d.asked_date, h.title as homework_title FROM doubts d JOIN homework h ON d.homework_id = h.id WHERE d.student_id = ?"
    params = [student_id]

    if homework_id:
        query += " AND d.homework_id = ?"
        params.append(homework_id)

    query += " ORDER BY d.asked_date DESC"
    doubts = db.execute(query, params).fetchall()

    return jsonify({"ok": True, "doubts": [dict(d) for d in doubts]})

@app.route("/api/student/ask_doubt", methods=["POST"])
@login_required
@role_required('student')
def api_student_ask_doubt():
    db = get_db()
    user_id = session['user_id']
    student = db.execute("SELECT id FROM students WHERE user_id = ?", (user_id,)).fetchone()
    if not student:
        return jsonify({"ok": False, "message": "Student profile not found"}), 404
    student_id = student['id']

    data = request.get_json()
    homework_id = data.get('homework_id')
    question = data.get('question')

    if not homework_id or not question:
        return jsonify({"ok": False, "message": "Missing required fields"}), 400

    asked_date = datetime.now().strftime("%d-%m-%Y %H:%M")
    db.execute("INSERT INTO doubts (homework_id, student_id, question, asked_date) VALUES (?, ?, ?, ?)",
               (homework_id, student_id, question, asked_date))
    db.commit()

    return jsonify({"ok": True, "message": "Question submitted successfully!"})

@app.route("/api/homework")
@login_required
def api_get_homework():
    db = get_db()
    homeworks = db.execute("""
        SELECT h.id, h.title, s.name as subject
        FROM homework h
        JOIN subjects s ON h.subject_id = s.id
        ORDER BY h.posted_date DESC
    """).fetchall()
    return jsonify([dict(hw) for hw in homeworks])

# Teacher API Routes
@app.route("/api/teacher/dashboard_stats")
@login_required
def api_teacher_dashboard_stats():
    if session['role'] == 'student':
        return jsonify({"ok": False, "error": "Unauthorized"}), 403

    db = get_db()
    students_count = db.execute("SELECT COUNT(*) as count FROM students").fetchone()['count']
    subjects_count = db.execute("SELECT COUNT(*) as count FROM subjects").fetchone()['count']

    active_homeworks = db.execute("""
        SELECT COUNT(*) as count FROM homework
        WHERE substr(due_date,7,4)||'-'||substr(due_date,4,2)||'-'||substr(due_date,1,2) >= date('now')
    """).fetchone()['count']

    today = datetime.now().strftime("%d-%m-%Y")
    today_classes = db.execute("SELECT COUNT(DISTINCT subject_id) as count FROM subjects").fetchone()['count']
    classes_marked = db.execute("SELECT COUNT(DISTINCT subject_id) as count FROM attendance WHERE date = ?", (today,)).fetchone()['count']

    pending_submissions = db.execute("SELECT COUNT(*) as count FROM homework_submissions WHERE status = 'Pending'").fetchone()['count']
    to_grade = db.execute("SELECT COUNT(*) as count FROM homework_submissions WHERE status = 'Submitted'").fetchone()['count']

    unanswered_doubts = db.execute("SELECT COUNT(*) as count FROM doubts WHERE answer IS NULL OR answer = ''").fetchone()['count']
    total_doubts = db.execute("SELECT COUNT(*) as count FROM doubts").fetchone()['count']

    return jsonify({
        "ok": True,
        "students": {"total": students_count},
        "subjects": {"total": subjects_count},
        "homework": {
            "active": active_homeworks,
            "pending_submissions": pending_submissions,
            "to_grade": to_grade
        },
        "attendance": {
            "today_classes": today_classes,
            "marked": classes_marked
        },
        "doubts": {
            "unanswered": unanswered_doubts,
            "total": total_doubts
        }
    })

@app.route("/api/teacher/doubts")
@login_required
def api_teacher_doubts():
    if session['role'] == 'student':
        return jsonify({"ok": False, "error": "Unauthorized"}), 403

    db = get_db()
    status = request.args.get('status', 'all')
    homework_id = request.args.get('homework_id', type=int)

    query = """
        SELECT d.id, d.question, d.answer, d.asked_date,
               s.name as student_name, h.title as homework_title
        FROM doubts d
        JOIN students s ON d.student_id = s.id
        JOIN homework h ON d.homework_id = h.id
        WHERE 1=1
    """
    params = []

    if status == 'unanswered':
        query += " AND (d.answer IS NULL OR d.answer = '')"
    elif status == 'answered':
        query += " AND d.answer IS NOT NULL AND d.answer != ''"

    if homework_id:
        query += " AND d.homework_id = ?"
        params.append(homework_id)

    query += " ORDER BY d.asked_date DESC"
    doubts = db.execute(query, params).fetchall()

    total = len(doubts)
    answered = sum(1 for d in doubts if d['answer'])
    unanswered = total - answered

    return jsonify({
        "ok": True,
        "doubts": [dict(d) for d in doubts],
        "stats": {
            "total": total,
            "answered": answered,
            "unanswered": unanswered
        }
    })

@app.route("/api/teacher/analytics")
@login_required
def api_teacher_analytics():
    if session['role'] == 'student':
        return jsonify({"ok": False, "error": "Unauthorized"}), 403

    db = get_db()

    attendance_data = db.execute("""
        SELECT
            SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present,
            SUM(CASE WHEN status = 'Absent Informed' THEN 1 ELSE 0 END) as absent_informed,
            SUM(CASE WHEN status = 'Absent Uninformed' THEN 1 ELSE 0 END) as absent_uninformed
        FROM attendance
    """).fetchone()

    homework_data = db.execute("""
        SELECT
            SUM(CASE WHEN status = 'Pending' THEN 1 ELSE 0 END) as pending,
            SUM(CASE WHEN status = 'Submitted' THEN 1 ELSE 0 END) as submitted,
            SUM(CASE WHEN status = 'Graded' THEN 1 ELSE 0 END) as graded
        FROM homework_submissions
    """).fetchone()

    subjects_data = db.execute("""
        SELECT
            s.name,
            COUNT(DISTINCT a.date) as classes,
            COUNT(DISTINCT CASE WHEN a.status = 'Present' THEN a.student_id END) * 100.0 / NULLIF(COUNT(*), 0) as avg_attendance,
            COUNT(DISTINCT h.id) as homeworks_count,
            AVG(hs.grade) as avg_grade,
            COUNT(DISTINCT CASE WHEN d.answer IS NULL OR d.answer = '' THEN d.id END) as pending_doubts
        FROM subjects s
        LEFT JOIN attendance a ON s.id = a.subject_id
        LEFT JOIN homework h ON s.id = h.subject_id
        LEFT JOIN homework_submissions hs ON h.id = hs.homework_id
        LEFT JOIN doubts d ON h.id = d.homework_id
        GROUP BY s.id, s.name
    """).fetchall()

    total_classes = db.execute("SELECT COUNT(DISTINCT date || subject_id) as count FROM attendance").fetchone()['count']
    total_homeworks = db.execute("SELECT COUNT(*) as count FROM homework").fetchone()['count']
    avg_grade = db.execute("SELECT AVG(grade) as avg FROM homework_submissions WHERE grade IS NOT NULL").fetchone()['avg']

    total_attendance = attendance_data['present'] + attendance_data['absent_informed'] + attendance_data['absent_uninformed']
    avg_attendance = 0
    if total_attendance > 0:
        avg_attendance = round((attendance_data['present'] / total_attendance) * 100, 1)

    low_performers = db.execute("""
        SELECT s.name, s.roll_no,
               COUNT(DISTINCT CASE WHEN a.status = 'Present' THEN a.id END) * 100.0 / NULLIF(COUNT(DISTINCT a.id), 0) as attendance_pct,
               AVG(hs.grade) as avg_grade
        FROM students s
        LEFT JOIN attendance a ON s.id = a.student_id
        LEFT JOIN homework_submissions hs ON s.id = hs.student_id
        GROUP BY s.id, s.name, s.roll_no
        HAVING attendance_pct < 75 OR avg_grade < 60
    """).fetchall()

    low_performers_list = []
    for student in low_performers:
        reasons = []
        if student['attendance_pct'] and student['attendance_pct'] < 75:
            reasons.append(f"Low attendance: {student['attendance_pct']:.1f}%")
        if student['avg_grade'] and student['avg_grade'] < 60:
            reasons.append(f"Low grades: {student['avg_grade']:.1f}")
        low_performers_list.append({
            "name": student['name'],
            "roll_no": student['roll_no'],
            "reasons": reasons
        })

    return jsonify({
        "ok": True,
        "attendance": dict(attendance_data),
        "homework": dict(homework_data),
        "subjects": [{
            "name": s['name'],
            "avg_attendance": round(s['avg_attendance'] or 0, 1),
            "homeworks_count": s['homeworks_count'] or 0,
            "avg_grade": round(s['avg_grade'] or 0, 1) if s['avg_grade'] else None,
            "pending_doubts": s['pending_doubts'] or 0
        } for s in subjects_data],
        "overall": {
            "total_classes": total_classes,
            "total_homeworks": total_homeworks,
            "avg_attendance": avg_attendance,
            "avg_grade": round(avg_grade, 1) if avg_grade else None
        },
        "low_performers": low_performers_list
    })

@app.route("/api/teacher/performance")
@login_required
def api_teacher_performance():
    if session['role'] == 'student':
        return jsonify({"ok": False, "error": "Unauthorized"}), 403

    db = get_db()
    metric = request.args.get('metric', 'attendance')

    if metric == 'attendance':
        students = db.execute("""
            SELECT s.name, s.roll_no,
                   COUNT(DISTINCT CASE WHEN a.status = 'Present' THEN a.id END) * 100.0 / NULLIF(COUNT(DISTINCT a.id), 0) as score
            FROM students s
            LEFT JOIN attendance a ON s.id = a.student_id
            GROUP BY s.id, s.name, s.roll_no
            ORDER BY score DESC
        """).fetchall()
        unit = '%'
    elif metric == 'homework':
        students = db.execute("""
            SELECT s.name, s.roll_no, AVG(hs.grade) as score
            FROM students s
            LEFT JOIN homework_submissions hs ON s.id = hs.student_id
            WHERE hs.grade IS NOT NULL
            GROUP BY s.id, s.name, s.roll_no
            ORDER BY score DESC
        """).fetchall()
        unit = ''
    else:
        students = db.execute("""
            SELECT s.name, s.roll_no, COUNT(d.id) as score
            FROM students s
            LEFT JOIN doubts d ON s.id = d.student_id
            GROUP BY s.id, s.name, s.roll_no
            ORDER BY score DESC
        """).fetchall()
        unit = ' questions'

    return jsonify({
        "ok": True,
        "students": [{
            "name": s['name'],
            "roll_no": s['roll_no'],
            "score": round(s['score'] or 0, 1),
            "unit": unit
        } for s in students]
    })

@app.route("/api/student/submit_homework", methods=["POST"])
@login_required
@role_required('student')
def api_student_submit_homework():
    db = get_db()
    user_id = session['user_id']
    student = db.execute("SELECT id FROM students WHERE user_id = ?", (user_id,)).fetchone()
    if not student:
        return jsonify({"ok": False, "message": "Student profile not found"}), 404
    student_id = student['id']

    data = request.get_json()
    homework_id = data.get('homework_id')
    status = data.get('status', 'Submitted')

    if not homework_id:
        return jsonify({"ok": False, "message": "Missing homework_id"}), 400

    db.execute("""
        INSERT INTO homework_submissions (homework_id, student_id, status)
        VALUES (?, ?, ?)
        ON CONFLICT(homework_id, student_id)
        DO UPDATE SET status = excluded.status
    """, (homework_id, student_id, status))
    db.commit()

    return jsonify({"ok": True, "message": "Homework status updated!"})

@app.route("/api/student/grade/<int:homework_id>")
@login_required
@role_required('student')
def api_student_grade(homework_id):
    db = get_db()
    user_id = session['user_id']
    student = db.execute("SELECT id FROM students WHERE user_id = ?", (user_id,)).fetchone()
    if not student:
        return jsonify({"ok": False, "error": "Student profile not found"}), 404
    student_id = student['id']

    submission = db.execute("""
        SELECT grade FROM homework_submissions
        WHERE homework_id = ? AND student_id = ?
    """, (homework_id, student_id)).fetchone()

    grade = submission['grade'] if submission else None

    return jsonify({"ok": True, "grade": grade})


if __name__ == "__main__":
    with app.app_context():
        print("Initializing database...")
        init_db()
    print("Starting Flask server...")
    app.run(debug=True, port=5001)