from flask import Flask, request, session, jsonify, send_from_directory, Response
import sqlite3

app = Flask(__name__)
app.secret_key = "super-secret-key-change-this"  # Change to a strong key!

DB_NAME = "database.db"
# Your admin credentials:
ADMIN_USER = "DEPT_CSE"
ADMIN_PASS = "381975"

students = [
    # Add **all registration numbers and names** here!
    ('23KD1A05D3', 'M BHARGAVI'), ('23KD1A05D4', 'M PRAVALLIKA'), ('23KD1A05D5', 'M VARAPRASAD'),
    ('23KD1A05D6', 'M MEGHANA'),   ('23KD1A05D7', 'M SWETHA'),     ('23KD1A05D8', 'M ABHINAV'),
    ('23KD1A05D9', 'M NAVYATHA'),  ('23KD1A05E0', 'M SINDHUJA'),   ('23KD1A05E1', 'M PRANATHI'),
    ('23KD1A05E2', 'M HARSHITHA'), ('23KD1A05E3', 'M SHARMILA'),   ('23KD1A05E4', 'M SHAILAJA'),
    ('23KD1A05E5', 'MOHSIN ALI'),  ('23KD1A05E6', 'M FARHEEN BEGUM'), ('23KD1A05E7', 'M VAMSI KRISHNA'),
    ('23KD1A05E8', 'M MADHURI'),   ('23KD1A05E9', 'M SARAYU SRI'), ('23KD1A05F0', 'M YUVA KIRAN'),
    ('23KD1A05F1', 'M JYOTHSNA'),  ('23KD1A05F2', 'M BENSON'),     ('23KD1A05F3', 'M BHARAT'),
    ('23KD1A05F4', 'M MANOJ KUMAR'), ('23KD1A05F5', 'N DEVI'),     ('23KD1A05F6', 'N ADHARSH'),
    ('23KD1A05F7', 'N SUBHASH'),   ('23KD1A05F9', 'N PRAVEEN KUMAR'), ('23KD1A05G0', 'N KYATHI'),
    ('23KD1A05G1', 'N PRANATHI'),  ('23KD1A05G2', 'N HARI CHARAN'), ('23KD1A05G3', 'NANADHINI M'),
    ('23KD1A05G4', 'N CHANIKYA'),  ('23KD1A05G5', 'N MEGHANA'),   ('23KD1A05G6', 'N SAITEJA'),
    ('23KD1A05G7', 'N DRAKSHAMANI'), ('23KD1A05G8', 'N LAVANYA'), ('23KD1A05G9', 'N AISHWARYA'),
    ('23KD1A05H0', 'N GEETHA'),    ('23KD1A05H1', 'P CHIDVILAS'), ('23KD1A05H2', 'P KIRAN'),
    ('23KD1A05H3', 'P HARISHANKAR'), ('23KD1A05H4', 'P SAIKIRAN'), ('23KD1A05H5', 'PVS POORNANANDA'),
    ('23KD1A05H7', 'P GEETHASRI'), ('23KD1A05H8', 'P KAVITHA'),   ('23KD1A05I0', 'P VINEELA'),
    ('23KD1A05I1', 'P SUMANTH'),   ('23KD1A05I2', 'P GEETHANJALI'), ('23KD1A05I3', 'P DEEPIKA'),
    ('23KD1A05I4', 'P AMRUTHA'),   ('23KD1A05I6', 'P SRIVALLI'),   ('23KD1A05I7', 'P JAHNAVI'),
    ('23KD1A05I8', 'P SURENDRA REDDY'), ('23KD1A05I9', 'P SRAVYA'), ('23KD1A05J0', 'P SAHITH'),
    ('23KD1A05J1', 'P BHAVYA SRI'), ('23KD1A05J2', 'P MEENAKSHI'), ('23KD1A05J3', 'P PRIYANKA'),
    ('23KD1A05J4', 'P CHITTI BABU'), ('23KD1A05J5', 'P MYTHRI'),  ('23KD1A05J6', 'JAHNAVI LATHA'),
    ('23KD1A05J8', 'P VARUDHINI')
]

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL
        )
    """)
    c.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            date TEXT,
            status TEXT,
            FOREIGN KEY(student_id) REFERENCES students(student_id)
        )
    """)
    conn.commit()
    c.executemany(
        "INSERT OR IGNORE INTO students (student_id, name) VALUES (?, ?)", students
    )
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def serve_frontend():
    return send_from_directory('.', 'frontend.html')

@app.route('/students', methods=['GET'])
def get_students():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT student_id, name FROM students ORDER BY student_id")
    result = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(result)

@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    if data.get('username') == ADMIN_USER and data.get('password') == ADMIN_PASS:
        session['admin'] = True
        return jsonify({'ok': True})
    return jsonify({'ok': False, 'error': 'Wrong username or password'}), 403

@app.route('/admin/logout', methods=['POST'])
def admin_logout():
    session.pop('admin', None)
    return jsonify({'ok': True})

def is_admin():
    return session.get('admin', False)

@app.route('/attendance', methods=['POST'])
def mark_attendance():
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    student_id = data.get('student_id')
    date = data.get('date')
    status = data.get('status')
    if not student_id or not date or not status:
        return jsonify({'error': 'Missing fields'}), 400
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM attendance WHERE student_id=? AND date=?", (student_id, date))
    if c.fetchone():
        conn.close()
        return jsonify({'error': 'Attendance already marked for this date'}), 400
    c.execute("INSERT INTO attendance (student_id, date, status) VALUES (?, ?, ?)", (student_id, date, status))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Attendance marked'}), 201

@app.route('/attendance', methods=['GET'])
def list_attendance():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        SELECT a.id, a.student_id, s.name, a.date, a.status
        FROM attendance a
        JOIN students s ON a.student_id = s.student_id
        ORDER BY a.date DESC, a.student_id ASC
    """)
    result = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(result)

@app.route('/attendance/filter', methods=['GET'])
def filter_attendance():
    date = request.args.get('date')
    student_id = request.args.get('student_id')
    conn = get_db_connection()
    c = conn.cursor()
    query = """
        SELECT a.id, a.student_id, s.name, a.date, a.status
        FROM attendance a JOIN students s ON a.student_id = s.student_id
        WHERE 1=1
    """
    params = []
    if date:
        query += " AND a.date = ?"
        params.append(date)
    if student_id:
        query += " AND a.student_id = ?"
        params.append(student_id)
    query += " ORDER BY a.date DESC, a.student_id ASC"
    c.execute(query, params)
    records = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify(records)

@app.route('/attendance/export', methods=['GET'])
def export_attendance():
    if not is_admin():
        return jsonify({'error': 'Unauthorized'}), 403
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""
        SELECT a.student_id, s.name, a.date, a.status
        FROM attendance a JOIN students s ON a.student_id = s.student_id
        ORDER BY a.date, a.student_id
    """)
    rows = c.fetchall()
    conn.close()
    def generate():
        yield 'Registration Number,Name,Date,Status\n'
        for row in rows:
            yield f"{row[0]},{row[1]},{row[2]},{row[3]}\n"
    return Response(generate(), mimetype='text/csv',
        headers={"Content-Disposition": "attachment;filename=attendance_export.csv"})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
