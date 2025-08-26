import mysql.connector
from config import DB_CONFIG

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

def create_user(name, email, password, role, specialty=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO users (name, email, password, role, specialty)
        VALUES (%s, %s, %s, %s, %s)
    """, (name, email, password, role, specialty))
    conn.commit()
    cursor.close()
    conn.close()

def add_pharmacy(name, location, hours, user_id, latitude=None, longitude=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO pharmacies (name, location, hours, user_id, latitude, longitude)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (name, location, hours, user_id, latitude, longitude))
    conn.commit()
    cursor.close()
    conn.close()

def get_user_by_credentials(email, password):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM users WHERE email = %s AND password = %s
    """, (email, password))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def get_doctors():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, specialty FROM users WHERE role='doctor'")
    doctors = cursor.fetchall()
    cursor.close()
    conn.close()
    return doctors

def create_appointment(patient_id, doctor_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO appointments (patient_id, doctor_id, status)
        VALUES (%s, %s, 'pending')
    """, (patient_id, doctor_id))
    conn.commit()
    cursor.close()
    conn.close()

def get_doctor_appointments(doctor_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.id, u.name as patient_name, a.status
        FROM appointments a
        JOIN users u ON a.patient_id = u.id
        WHERE a.doctor_id = %s
        ORDER BY a.id DESC
    """, (doctor_id,))
    appointments = cursor.fetchall()
    cursor.close()
    conn.close()
    return appointments

def get_patient_appointments(patient_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.id, u.name as doctor_name, a.status
        FROM appointments a
        JOIN users u ON a.doctor_id = u.id
        WHERE a.patient_id = %s
        ORDER BY a.id DESC
    """, (patient_id,))
    appointments = cursor.fetchall()
    cursor.close()
    conn.close()
    return appointments

def update_appointment_status(appointment_id, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE appointments SET status=%s WHERE id=%s
    """, (status, appointment_id))
    conn.commit()
    cursor.close()
    conn.close()

def get_pharmacies():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, location, hours, user_id, latitude, longitude FROM pharmacies")
    pharmacies = cursor.fetchall()
    cursor.close()
    conn.close()
    return pharmacies

def get_medicines_by_pharmacy(pharmacy_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM medicines WHERE pharmacy_id=%s", (pharmacy_id,))
    medicines = cursor.fetchall()
    cursor.close()
    conn.close()
    return medicines

def get_articles():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM articles")
    articles = cursor.fetchall()
    cursor.close()
    conn.close()
    return articles

def get_forum_posts():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM forum ORDER BY created_at DESC")
    posts = cursor.fetchall()
    cursor.close()
    conn.close()
    return posts

def add_forum_post(user_id, question):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO forum (user_id, question) VALUES (%s, %s)", (user_id, question))
    conn.commit()
    cursor.close()
    conn.close()

def get_pharmacy_by_id(pharmacy_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM pharmacies WHERE id=%s", (pharmacy_id,))
    pharmacy = cursor.fetchone()
    cursor.close()
    conn.close()
    return pharmacy

def create_medicine_order(patient_id, pharmacy_id, medicine_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO medicine_orders (patient_id, pharmacy_id, medicine_id, status)
        VALUES (%s, %s, %s, 'pending')
    """, (patient_id, pharmacy_id, medicine_id))
    conn.commit()
    cursor.close()
    conn.close()

def get_pharmacy_orders(pharmacy_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT o.id, o.status, o.message, o.created_at, u.name as patient_name, m.name as medicine_name
        FROM medicine_orders o
        JOIN users u ON o.patient_id = u.id
        JOIN medicines m ON o.medicine_id = m.id
        WHERE o.pharmacy_id = %s
        ORDER BY o.id DESC
    """, (pharmacy_id,))
    orders = cursor.fetchall()
    cursor.close()
    conn.close()
    return orders

def get_patient_orders(patient_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT o.id, o.status, o.message, o.created_at, p.name as pharmacy_name, m.name as medicine_name
        FROM medicine_orders o
        JOIN pharmacies p ON o.pharmacy_id = p.id
        JOIN medicines m ON o.medicine_id = m.id
        WHERE o.patient_id = %s
        ORDER BY o.id DESC
    """, (patient_id,))
    orders = cursor.fetchall()
    cursor.close()
    conn.close()
    return orders

def update_order_status(order_id, status, message):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE medicine_orders SET status=%s, message=%s WHERE id=%s
    """, (status, message, order_id))
    conn.commit()
    cursor.close()
    conn.close()

def add_forum_question(user_id, question, anonymous):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO forum_questions (user_id, question, anonymous)
        VALUES (%s, %s, %s)
    """, (user_id, question, anonymous))
    conn.commit()
    cursor.close()
    conn.close()

def get_forum_questions_with_answers():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT fq.id, fq.question, fq.anonymous, fq.created_at,
               fq.user_id, u.name as patient_name
        FROM forum_questions fq
        LEFT JOIN users u ON fq.user_id = u.id
        ORDER BY fq.created_at DESC
    """)
    questions = cursor.fetchall()
    # Get answers for each question
    for q in questions:
        cursor.execute("""
            SELECT fa.answer, fa.created_at, d.name as doctor_name
            FROM forum_answers fa
            JOIN users d ON fa.doctor_id = d.id
            WHERE fa.question_id = %s
            ORDER BY fa.created_at ASC
        """, (q['id'],))
        q['answers'] = cursor.fetchall()
    cursor.close()
    conn.close()
    return questions

def add_forum_answer(question_id, doctor_id, answer):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO forum_answers (question_id, doctor_id, answer)
        VALUES (%s, %s, %s)
    """, (question_id, doctor_id, answer))
    conn.commit()
    cursor.close()
    conn.close()

def add_medicine(pharmacy_id, name, stock, price):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO medicines (pharmacy_id, name, stock, price)
        VALUES (%s, %s, %s, %s)
    """, (pharmacy_id, name, stock, price))
    conn.commit()
    cursor.close()
    conn.close()

def remove_medicine(medicine_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM medicines WHERE id=%s", (medicine_id,))
    conn.commit()
    cursor.close()
    conn.close()
