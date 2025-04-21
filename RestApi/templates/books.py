import psycopg2
import random

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    host="localhost",
    database="tradetales",
    user="myuser",
    password="mypassword"
)
cursor = conn.cursor()

# Generate random prices for all books
try:
    cursor.execute("SELECT book_id FROM books")
    books = cursor.fetchall()

    for book in books:
        book_id = book[0]
        random_price = round(random.uniform(5.00, 50.00), 2)  # Generate a random price between $5.00 and $50.00
        cursor.execute("UPDATE books SET price = %s WHERE book_id = %s", (random_price, book_id))

    conn.commit()
    print("Random prices have been assigned to all books.")
except Exception as e:
    conn.rollback()
    print(f"Error updating prices: {e}")
finally:
    cursor.close()
    conn.close()