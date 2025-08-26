from flask import Flask, render_template, request, redirect, session, flash
from dotenv import load_dotenv
import os
load_dotenv()
from db_models import (
    get_doctor_appointments,
    get_patient_appointments,
    get_user_by_credentials,
    create_user,
    get_doctors,
    create_appointment,
    update_appointment_status,
    get_pharmacies,
    get_medicines_by_pharmacy,
    get_articles,
    get_pharmacy_by_id,
    add_pharmacy,
    get_db_connection,
    create_medicine_order,
    get_pharmacy_orders,
    get_patient_orders,
    update_order_status,
    add_forum_question,
    get_forum_questions_with_answers,
    add_forum_answer
)

app = Flask(__name__)
app.secret_key = 'your_secret_key'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        specialty = request.form.get('specialty') if role == 'doctor' else None

        if role == 'pharmacy':
            pharmacy_name = request.form.get('pharmacy_name')
            location = request.form.get('location')
            hours = request.form.get('hours')
            latitude = request.form.get('latitude')
            longitude = request.form.get('longitude')
            latitude = float(latitude) if latitude and latitude.strip() != "" else None
            longitude = float(longitude) if longitude and longitude.strip() != "" else None
            try:
                create_user(name, email, password, role)
                user = get_user_by_credentials(email, password)
                add_pharmacy(pharmacy_name, location, hours, user['id'], latitude, longitude)
                flash('Pharmacy account created! Please login.', 'success')
                return redirect('/login')
            except Exception as e:
                flash('Signup failed: ' + str(e), 'danger')
        else:
            try:
                create_user(name, email, password, role, specialty)
                flash('Account created! Please login.', 'success')
                return redirect('/login')
            except Exception as e:
                flash('Signup failed: ' + str(e), 'danger')
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = get_user_by_credentials(email, password)
        if user:
            session['user_id'] = user['id']
            session['role'] = user['role']
            session['name'] = user['name']
            flash('Login successful!', 'success')
            return redirect('/dashboard')
        else:
            flash('Invalid credentials', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    role = session.get('role')
    if role == 'doctor':
        appointments = get_doctor_appointments(session['user_id'])
        return render_template('dashboard_doctor.html', name=session['name'], appointments=appointments)
    elif role == 'pharmacy':
        pharmacies = get_pharmacies()
        my_pharmacy = None
        for pharmacy in pharmacies:
            if str(pharmacy.get('user_id')) == str(session['user_id']):
                my_pharmacy = pharmacy
                break
        medicines = get_medicines_by_pharmacy(my_pharmacy['id']) if my_pharmacy else []
        orders = get_pharmacy_orders(my_pharmacy['id']) if my_pharmacy else []
        return render_template('dashboard_pharmacy.html', name=session['name'], pharmacy=my_pharmacy, medicines=medicines, orders=orders)
    else:
        doctors = get_doctors()
        appointments = get_patient_appointments(session['user_id'])
        orders = get_patient_orders(session['user_id'])
        return render_template('dashboard_patient.html', name=session['name'], doctors=doctors, appointments=appointments, orders=orders)
    
@app.route('/book', methods=['POST'])
def book():
    if 'user_id' not in session or session.get('role') != 'patient':
        return redirect('/login')
    doctor_id = request.form['doctor_id']
    patient_id = session['user_id']
    create_appointment(patient_id, doctor_id)
    flash('Appointment requested!', 'success')
    return redirect('/dashboard')

@app.route('/appointment_action', methods=['POST'])
def appointment_action():
    if 'user_id' not in session or session.get('role') != 'doctor':
        return redirect('/login')
    appointment_id = request.form['appointment_id']
    action = request.form['action']
    if action == 'confirm':
        update_appointment_status(appointment_id, 'confirmed')
        flash('Appointment confirmed.', 'success')
    elif action == 'decline':
        update_appointment_status(appointment_id, 'declined')
        flash('Appointment declined.', 'warning')
    return redirect('/dashboard')

@app.route('/pharmacies')
def pharmacies():
    pharmacies = get_pharmacies()
    return render_template('pharmacies.html', pharmacies=pharmacies)

@app.route('/pharmacy/<int:pharmacy_id>')
def pharmacy_detail(pharmacy_id):
    pharmacy = get_pharmacy_by_id(pharmacy_id)
    medicines = get_medicines_by_pharmacy(pharmacy_id)
    return render_template('pharmacy_profile.html', pharmacy=pharmacy, medicines=medicines)

@app.route('/order_medicine', methods=['POST'])
def order_medicine():
    if 'user_id' not in session or session.get('role') != 'patient':
        return redirect('/login')
    pharmacy_id = request.form['pharmacy_id']
    medicine_id = request.form['medicine_id']
    patient_id = session['user_id']
    create_medicine_order(patient_id, pharmacy_id, medicine_id)
    flash('Medicine order placed!', 'success')
    return redirect('/dashboard')

@app.route('/order_action', methods=['POST'])
def order_action():
    if 'user_id' not in session or session.get('role') != 'pharmacy':
        return redirect('/login')
    order_id = request.form['order_id']
    action = request.form['action']
    message = request.form.get('message', '')
    if action == 'approve':
        update_order_status(order_id, 'approved', message)
        flash('Order approved.', 'success')
    elif action == 'decline':
        update_order_status(order_id, 'declined', message)
        flash('Order declined.', 'warning')
    return redirect('/dashboard')

@app.route('/health-education')
def health_education():
    return render_template('health_education.html')

from groq import Groq

@app.route('/symptom_checker', methods=['GET', 'POST'])
def symptom_checker():
    advice = None
    if request.method == 'POST':
        symptoms = request.form['symptoms']
        api_key = os.getenv("GROQ_API_KEY")
        client = Groq(api_key=api_key)
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "user",
                    "content": symptoms
                }
            ],
            temperature=1,
            max_completion_tokens=1024,
            top_p=1,
            stream=False,
            stop=None
        )
        advice = completion.choices[0].message.content
    return render_template('symptom_checker.html', advice=advice)

@app.route('/forum', methods=['GET', 'POST'])
def forum():
    role = session.get('role')
    user_id = session.get('user_id')
    if request.method == 'POST':
        if role == 'patient':
            question = request.form['question']
            anonymous = bool(request.form.get('anonymous'))
            add_forum_question(user_id, question, anonymous)
            flash('Question posted!', 'success')
            return redirect('/forum')
        elif role == 'doctor':
            question_id = request.form['question_id']
            answer = request.form['answer']
            add_forum_answer(question_id, user_id, answer)
            flash('Answer posted!', 'success')
            return redirect('/forum')
    questions = get_forum_questions_with_answers()
    return render_template('forum.html', questions=questions, role=role)

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'info')
    return redirect('/')

@app.route('/add_medicine', methods=['POST'])
def add_medicine():
    if 'user_id' not in session or session.get('role') != 'pharmacy':
        return redirect('/login')
    pharmacy_id = request.form['pharmacy_id']
    name = request.form['name']
    stock = request.form['stock']
    price = request.form['price']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO medicines (pharmacy_id, name, stock, price)
        VALUES (%s, %s, %s, %s)
    """, (pharmacy_id, name, stock, price))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Medicine added!', 'success')
    return redirect('/dashboard')

@app.route('/remove_medicine', methods=['POST'])
def remove_medicine():
    if 'user_id' not in session or session.get('role') != 'pharmacy':
        return redirect('/login')
    medicine_id = request.form['medicine_id']
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM medicines WHERE id=%s", (medicine_id,))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Medicine removed!', 'success')
    return redirect('/dashboard')

if __name__ == "__main__":
    app.run(debug=True)


# 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