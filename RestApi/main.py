from flask import Flask, render_template, request, jsonify
import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt

app = Flask(__name__)

# Database Credentials
DB_NAME = "tradetales"
DB_USER = "myuser"
DB_PASSWORD = "mypassword"
DB_HOST = "localhost"
DB_PORT = "5432"

# Function to get DB connection
def get_db_connection():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT,
            cursor_factory=RealDictCursor
        )
        print("✅ Connected to Database")
        return conn
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return None

# Check database connection at startup
db_conn = get_db_connection()
if db_conn:
    db_conn.close()

@app.route("/")
def home():
    return render_template("dashboard.html")  # Load dashboard first

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/login")
def login_page():
    return render_template("login.html")  # Redirects to login page

@app.route("/login", methods=["POST"])
def login():
    try:
        data = request.json
        username = data.get("username")
        password = data.get("password")

        conn = get_db_connection()
        if not conn:
            return jsonify({"message": "Database connection failed", "status": "error"}), 500

        cursor = conn.cursor()
        cursor.execute("SELECT username, password FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        conn.close()

        if not user:
            return jsonify({"message": "User not found!", "status": "error"}), 404

        stored_password = user["password"]  # Directly fetch password

        if password == stored_password:  # Compare directly
            return jsonify({"message": "Login Successful!", "status": "success"}), 200

        return jsonify({"message": "Invalid Credentials!", "status": "error"}), 401
    except Exception as e:
        return jsonify({"message": f"Error: {str(e)}", "status": "error"}), 500

if __name__ == "__main__":
    app.run(debug=True)
