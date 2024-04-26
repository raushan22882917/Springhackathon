
from flask import Flask, render_template, request, redirect, url_for, session,jsonify,render_template_string
import psycopg2
import google.generativeai as genai
import numpy as np
import pickle
import google.generativeai as genai
app = Flask(__name__, template_folder='templates')

app.secret_key = '/x08XA4/xae/xa3->/xf6/x00/x8c?/xe3/x1b/xa7p/x1f/xd0/x03/x172/xd8w/x13'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


@app.route('/')
def home():
    return render_template('index.html')



# About page route
@app.route('/about')
def about():
    if 'loggedin' in session:
        return render_template('about.html')
    else:
        return redirect(url_for('login'))

# Contact page route
@app.route('/contact')
def contact():
    if 'loggedin' in session:
        return render_template('contact.html')
    else:
        return redirect(url_for('login'))

# Articles page route
@app.route('/articles')
def Articles():
    if 'loggedin' in session:
        return render_template('symptoms.html')
    else:
        return redirect(url_for('login'))

# Department page route
@app.route('/department')
def department():
    if 'loggedin' in session:
        return render_template('departments.html')
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    # Clear the session to log out the user
    session.clear()
    return redirect(url_for('index'))


# Database connection parameters
DB_NAME = 'medical'
DB_USER = 'postgres'
DB_PASSWORD = '22882288'
DB_HOST = 'localhost'
DB_PORT = '5432'

# Function to establish database connection
def connect_db():
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    return conn

# Registration page
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        unique_id = request.form['unique_id']
        phone_number = request.form['phone_number']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        address = request.form['address']

        if password != confirm_password:
            return "Passwords do not match. Please try again."

        # Connect to the database
        conn = connect_db()
        cur = conn.cursor()

        # Check if the unique ID already exists
        cur.execute("SELECT * FROM patients WHERE unique_id = %s", (unique_id,))
        if cur.fetchone():
            return "This unique ID is already registered. Please choose another one."

        # Insert new patient into the database
        cur.execute("INSERT INTO patients (name, email, unique_id, phone_number, password, address) VALUES (%s, %s, %s, %s, %s, %s)",
                    (name, email, unique_id, phone_number, password, address))
        conn.commit()
        conn.close()
        
        # Send registration confirmation email
        return redirect(url_for('login'))
    return render_template('register.html')


# Login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        unique_id = request.form['unique_id']
        password = request.form['password']

        # Connect to the database
        conn = connect_db()
        cur = conn.cursor()

        # Check if the unique ID and password match
        cur.execute("SELECT * FROM patients WHERE unique_id = %s AND password = %s", (unique_id, password))
        patient = cur.fetchone()
        conn.close()
        if patient:
            # Store patient's name in session
            session["loggedin"] = True
            session["unique_id"] = unique_id
            return redirect(url_for('home'))
        else:
            error = "Invalid unique ID or password. Please try again."
            return render_template('login.html', error=error)

    return render_template('login.html')





    
loaded_model = pickle.load(open('trained_model.pkl', 'rb'))

@app.route('/diabetes')
def index():
    if 'loggedin' in session:
        return render_template('diabetes.html')
    else:
        return redirect(url_for('login'))


def get_user_name(unique_id):
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT name FROM patients WHERE unique_id = %s", (unique_id,))
    user = cur.fetchone()
    conn.close()
    return user[0] if user else None

def connect_to_database():
    conn = psycopg2.connect(
        dbname="medical",
        user="postgres",
        password="22882288",
        host="localhost",
        port="5432"
    )
    return conn





gemini_api_key = "AIzaSyBTc042cwNJZNyRUQcrUtoHr-LAzLcEA6o"
genai.configure(api_key=gemini_api_key)

model = genai.GenerativeModel("gemini-pro")                      
pincode = "226001"

@app.route('/hospital')
def generate_html():
    response = model.generate_content(f"Find nearby hospitals in {pincode} within a 10km radius, with expertise in managing diabetes cases. Provide their address, contact number, hospital website, Google Maps link, and all information in HTML format using only div, a, h1 to h6 tags. Ensure the presentation is enhanced with CSS styling, Bootstrap framework, and appropriate icons.")

    html_content = f"""
        <div class="container">
            <div class="row">
                <div class="col-md-6 offset-md-3">
                    <div class="card shadow-lg p-3 mb-5 bg-white rounded">
                        <div class="card-body">
                            <h3 class="card-title text-center mb-4">Nearby Hospitals</h3>
                            <div class="card-text">
                                {response.text}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    """

    
    return render_template_string(html_content)


conn = psycopg2.connect(
    dbname="medical",
    user="postgres",
    password="22882288",
    host="localhost"
)
cur = conn.cursor()

# Routes
@app.route('/feedback')
def feedback():
    return render_template('feedback.html')

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    username = request.form['username']
    feedback = request.form['feedback']
    cur.execute("INSERT INTO feedback (username, message) VALUES (%s, %s)", (username, feedback,))
    conn.commit()
    return 'Feedback submitted successfully!'

@app.route('/get_feedback')
def get_feedback():
    cur.execute("SELECT username, message FROM feedback")
    feedback = cur.fetchall()
    feedback = [{'username': row[0], 'message': row[1]} for row in feedback]
    return jsonify(feedback)


# PostgreSQL connection configuration
DB_HOST = 'localhost'
DB_NAME = 'medical'
DB_USER = 'postgres'
DB_PASSWORD = '22882288'

def create_connection():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST
        )
        return conn
    except psycopg2.Error as e:
        print("Error connecting to the database:", e)
        return None

@app.route('/doctor')
def doctor():
    return render_template('doctors.html')

@app.route('/register_doctor', methods=['POST'])
def register_doctor():
    full_name = request.form['full_name']
    email = request.form['email']
    specialization = request.form['specialization']
    hospital = request.form['hospital']
    location = request.form['location']
    address = request.form['address']
    contact = request.form['contact']

    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO doctors (full_name, email, specialization, hospital, location, address, contact) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                           (full_name, email, specialization, hospital, location, address, contact))
            conn.commit()
            cursor.close()
            conn.close()
            return redirect('/doctor')
        except psycopg2.Error as e:
            print("Error executing SQL query:", e)
            conn.rollback()
            conn.close()
            return "Error registering doctor"
    else:
        return "Database connection error"
    
# Define your database connection parameters
DB_HOST = 'localhost'
DB_NAME = 'medical'
DB_USER = 'postgres'
DB_PASSWORD = '22882288'

def create_connection():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST
        )
        return conn
    except psycopg2.Error as e:
        print("Error connecting to the database:", e)
        return None

@app.route('/data')
def data():
    conn = create_connection()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM doctors")
        doctors = cursor.fetchall()
        conn.close()
        return render_template('doc_data.html', doctors=doctors)
    else:
        return "Database connection error"
    
    

#############################################################################################



db_params = {
    'dbname': 'medical',
    'user': 'postgres',
    'password': '22882288',
    'host': 'localhost',
    'port': '5432'
}

# Route for the homepage
def diabetes_prediction(input_data):
    # Convert input_data to numpy array
    input_data_as_numpy_array = np.asarray(input_data)
    # Reshape the array for prediction
    input_data_reshaped = input_data_as_numpy_array.reshape(1, -1)
    prediction = loaded_model.predict(input_data_reshaped)

    if prediction[0] == 0:
        return 'The person is not diabetic'
    else:
        return 'The person is diabetic'
# Route to handle form submission and display prediction result
@app.route('/predict', methods=['POST'])
def predict():
    pregnancies = float(request.form['Pregnancies'])
    glucose = float(request.form['Glucose'])
    blood_pressure = float(request.form['BloodPressure'])
    skin_thickness = float(request.form['SkinThickness'])
    insulin = float(request.form['Insulin'])
    bmi = float(request.form['BMI'])
    diabetes_pedigree_function = float(request.form['DiabetesPedigreeFunction'])
    age = float(request.form['Age'])
    
    # Ensure the user is logged in
    if "unique_id" not in session:
        return redirect(url_for('login'))  # Redirect to login page if user is not logged in
    
    # Connect to the database
    conn = connect_db()
    cur = conn.cursor()
    
    # Insert data into the diabetes_prediction_data table
    cur.execute("""
        INSERT INTO diabetes_prediction_data 
        (unique_id, pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, diabetes_pedigree_function, age) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (session["unique_id"], pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, diabetes_pedigree_function, age))
    conn.commit()
    
    # Close the database connection
    cur.close()
    conn.close()
    
    # Call the diabetes_prediction function to get the diagnosis
    diagnosis = diabetes_prediction([pregnancies, glucose, blood_pressure, skin_thickness, insulin, bmi, diabetes_pedigree_function, age])

    # Render the result.html template and pass the prediction result
    return render_template('result.html', diagnosis=diagnosis)





DB_NAME = "medical"
DB_USER = "postgres"
DB_PASSWORD = "22882288"
DB_HOST = "localhost"
DB_PORT = "5432"

# Function to connect to the database
def connect_to_db():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        return conn
    except psycopg2.Error as e:
        print("Unable to connect to the database:", e)

# Route to fetch diabetes data and render HTML template
@app.route('/profile')
def profile():
    # Check if the user is logged in
    if "loggedin" in session:
        unique_id = session["unique_id"]  # Retrieve unique_id from session

        # Connect to the database
        conn = connect_to_db()
        if conn:
            cur = conn.cursor()

            # Retrieve user's details from the "patients" table using their unique_id
            cur.execute("SELECT * FROM patients WHERE unique_id = %s", (unique_id,))
            user_data = cur.fetchone()

            # Retrieve diabetes prediction data
            cur.execute("SELECT * FROM diabetes_prediction_data")
            diabetes_prediction_data = cur.fetchall()

            cur.close()
            conn.close()

            # Prepare data for rendering
            data = []
            for row in diabetes_prediction_data:
                data.append({
                    "unique_id": row[1],
                    "pregnancies": row[2],
                    "glucose": row[3],
                    "blood_pressure": row[4],
                    "skin_thickness": row[5],
                    "insulin": row[6],
                    "bmi": row[7],
                    "diabetes_pedigree_function": row[8],
                    "age": row[9],
                    "timestamp": row[10]
                    
                })

            # Pass user_data and diabetes_prediction_data to the profile.html template for rendering
            return render_template('profile.html', user_data=user_data, diabetes_prediction_data=data)
        else:
            return jsonify({"error": "Unable to connect to the database"})
    else:
        return redirect(url_for('login'))
if __name__ == '__main__':
    app.run(debug=True)
