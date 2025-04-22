import os
import psycopg2

# Determine the database connection dynamically
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    # Fallback for local development
    DATABASE_URL = "postgresql://myuser:mypassword@localhost:5432/tradetales"
elif "localhost" in DATABASE_URL:
    # Ensure localhost is used only for local development
    print("Using localhost for database connection.")
else:
    print("Using Docker database connection.")

# Debugging log to verify the DATABASE_URL
print(f"Connecting to database: {DATABASE_URL}")

# Connect to the database
try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    print("Database connection successful!")
except psycopg2.OperationalError as e:
    print(f"Error connecting to the database: {e}")
    raise