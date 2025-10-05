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
    return render_template("new_home.html", page="home")

@app.route("/attendance")
@login_required
def attendance_home():
    return render_template("attendance_home.html", page="attendance_home")

@app.route("/store")
@login_required
def store():
    # UPDATED: This now blocks students
    if session['role'] == 'student':
        flash("You do not have permission to access this page.", "danger")
        return redirect(url_for('home'))
    return render_template("store.html", page="store")

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


if __name__ == "__main__":
    with app.app_context():
        print("Initializing database...")
        init_db()
    print("Starting Flask server...")
    app.run(debug=True, port=5001)