from flask import Flask, render_template, request, jsonify
import psycopg2

app = Flask(__name__)

# Database Credentials
DB_NAME = "tradetales"
DB_USER = "myuser"
DB_PASSWORD = "mypassword"
DB_HOST = "localhost"
DB_PORT = "5432"

# Function to get DB connection
def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )

@app.route("/")
def home():
    return render_template("login.html")  # Renders login page

@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    conn = get_db_connection()
    cursor = conn.cursor()

    # Query to get the user by username
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    conn.close()

    if user:
        # Check if the plain text password matches the stored password
        if user[3] == password:  # user[3] corresponds to the stored password (plain text)
            return "Login Successful!"
        else:
            return "Invalid Credentials! Try Again."
    else:
        return "User not found! Try Again."

if __name__ == "__main__":
    print("Connecting to the database...")
    conn = get_db_connection()
    if conn:
        print("Database connected successfully!")
    else:
        print("Database connection failed!")
    app.run(debug=True)
