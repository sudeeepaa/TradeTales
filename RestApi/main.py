from fastapi import FastAPI, Request, Form, File, UploadFile, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
import psycopg2
import os
import shutil
from pathlib import Path

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key='your_secret_key')

# Mount static files
app.mount("/static", StaticFiles(directory="RestApi/static"), name="static")

# Templates folder
templates = Jinja2Templates(directory="RestApi/templates")

# PostgreSQL connection
conn = psycopg2.connect(
    host="localhost",
    database="tradetales",
    user="myuser",
    password="mypassword"
)
cursor = conn.cursor()


@app.get("/", response_class=HTMLResponse)
def user_dashboard(request: Request):
    username = request.session.get("user")
    if not username:
        return RedirectResponse(url="/login", status_code=302)

    # Fetch all books for browsing
    cursor.execute("""
        SELECT title, author, genre, description, cover_image, condition, trade_option, price, book_id
        FROM books
        ORDER BY created_at DESC
    """)
    available_books = cursor.fetchall()

    # Fetch the user's wishlist
    cursor.execute("""
        SELECT b.title, b.author, b.genre, b.description, b.cover_image, b.book_id
        FROM wishlist w
        JOIN books b ON w.book_id = b.book_id
        JOIN users u ON w.user_id = u.user_id
        WHERE u.username = %s
    """, (username,))
    wishlist_books = cursor.fetchall()

    # Fetch the user's uploaded books
    cursor.execute("""
        SELECT title, author, genre, description, cover_image, book_id, price
        FROM books
        WHERE user_id = (SELECT user_id FROM users WHERE username = %s)
        ORDER BY created_at DESC
    """, (username,))
    uploaded_books = cursor.fetchall()

    # Fetch the user's transactions
    cursor.execute("""
        SELECT b.title, b.price, t.transaction_date
        FROM transactions t
        JOIN books b ON t.book_id = b.book_id
        JOIN users u ON t.buyer_id = u.user_id
        WHERE u.username = %s
        ORDER BY t.transaction_date DESC
    """, (username,))
    transactions = cursor.fetchall()

    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "username": username,
        "available_books": available_books,
        "wishlist_books": wishlist_books,
        "uploaded_books": uploaded_books,
        "transactions": transactions
    })


@app.get("/login", response_class=HTMLResponse)
def login_get(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_class=HTMLResponse)
def login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    try:
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and user[0] == password:
            request.session['user'] = username
            return RedirectResponse(url="/", status_code=302)

        return templates.TemplateResponse("login.html", {"request": request, "message": "Invalid username or password"})
    except Exception as e:
        conn.rollback()  # Rollback the transaction
        print(f"Error during login: {e}")
        return templates.TemplateResponse("login.html", {"request": request, "message": "An error occurred during login."})


@app.get("/signup", response_class=HTMLResponse)
def signup_get(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})


@app.post("/signup", response_class=HTMLResponse)
def signup_post(request: Request, username: str = Form(...), email: str = Form(...), password: str = Form(...)):
    try:
        # Insert the new user into the database
        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
        conn.commit()

        # Automatically log in the user by storing their username in the session
        request.session['user'] = username

        # Redirect to the dashboard
        return RedirectResponse(url="/", status_code=302)
    except psycopg2.IntegrityError:
        conn.rollback()
        return templates.TemplateResponse("signup.html", {"request": request, "message": "User with this username or email already exists."})
    except Exception as e:
        conn.rollback()
        return templates.TemplateResponse("signup.html", {"request": request, "message": f"Signup failed: {e}"})


@app.get("/admin-login", response_class=HTMLResponse)
def admin_login_get(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})


@app.post("/admin-login", response_class=HTMLResponse)
def admin_login_post(request: Request, username: str = Form(...), password: str = Form(...)):
    print(f"Attempting login with username: {username}, password: {password}")
    if username == "admin" and password == "admin123":
        request.session['user'] = "admin"
        print("Admin login successful. Redirecting to /admin")
        return RedirectResponse(url="/admin", status_code=302)
    print("Invalid admin credentials")
    return templates.TemplateResponse("admin_login.html", {"request": request, "message": "Invalid admin credentials"})


@app.get("/admin", response_class=HTMLResponse)
def admin_dashboard(request: Request):
    user = request.session.get("user")
    if user != "admin":
        return RedirectResponse(url="/admin-login", status_code=302)

    # Fetch all users
    try:
        cursor.execute("""
            SELECT user_id, username, email, created_at FROM users
            ORDER BY user_id ASC
        """)
        users = cursor.fetchall()
    except Exception as e:
        users = []
        print(f"Error fetching users: {e}")

    # Fetch all books (include created_at column)
    try:
        cursor.execute("""
            SELECT book_id, title, author, genre, condition, created_at
            FROM books
            ORDER BY created_at DESC
        """)
        books = cursor.fetchall()
    except Exception as e:
        books = []
        print(f"Error fetching books: {e}")

    # Fetch all transactions
    try:
        cursor.execute("""
            SELECT transaction_id, status, transaction_date, book_id
            FROM transactions
            ORDER BY transaction_date DESC
        """)
        transactions = cursor.fetchall()
    except Exception as e:
        transactions = []
        print(f"Error fetching transactions: {e}")

    # Pass the data to the template
    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "users": users,
        "books": books,
        "transactions": transactions,
    })


@app.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=302)


@app.get("/book/{book_id}", response_class=HTMLResponse)
def book_details(request: Request, book_id: int):
    print(f"Fetching details for book_id: {book_id}")  # Debugging log
    cursor.execute("""
        SELECT title, author, genre, description, cover_image, condition, trade_option
        FROM books
        WHERE book_id = %s
    """, (book_id,))
    book = cursor.fetchone()
    print(f"Book details fetched: {book}")  # Debugging log
    if book:
        return templates.TemplateResponse("book_details.html", {
            "request": request,
            "book": {
                "title": book[0],
                "author": book[1],
                "genre": book[2],
                "description": book[3],
                "cover_image": book[4],
                "condition": book[5],
                "trade_option": book[6],
                "book_id": book_id
            }
        })
    else:
        return templates.TemplateResponse("book_details.html", {
            "request": request,
            "error": "Book not found."
        })


# Create the uploads directory if it doesn't exist
UPLOAD_DIR = Path("RestApi/static/books")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@app.get("/admin/add-book", response_class=HTMLResponse)
def admin_add_book(request: Request):
    user = request.session.get("user")
    if user != "admin":
        return RedirectResponse(url="/admin-login", status_code=302)
    return templates.TemplateResponse("admin_add_book.html", {"request": request})


@app.post("/admin/add-book", response_class=HTMLResponse)
async def admin_add_book_post(
    request: Request,
    title: str = Form(...),
    author: str = Form(...),
    genre: str = Form(...),
    description: str = Form(...),
    condition: str = Form(...),  # New field
    cover_image: UploadFile = File(...)
):
    file_location = UPLOAD_DIR / cover_image.filename
    with open(file_location, "wb") as f:
        shutil.copyfileobj(cover_image.file, f)

    try:
        cursor.execute("""
            INSERT INTO books (title, author, genre, description, condition, cover_image, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """, (title, author, genre, description, condition, f"books/{cover_image.filename}"))
        conn.commit()
        return RedirectResponse(url="/admin", status_code=302)
    except Exception as e:
        conn.rollback()
        return templates.TemplateResponse("admin_add_book.html", {"request": request, "message": f"Failed to add book: {str(e)}"})


@app.post("/admin/delete-book/{book_id}", response_class=HTMLResponse)
def delete_book(request: Request, book_id: int):
    try:
        cursor.execute("DELETE FROM books WHERE book_id = %s", (book_id,))
        conn.commit()
        return RedirectResponse(url="/admin", status_code=302)
    except Exception as e:
        conn.rollback()  # Rollback the transaction
        print(f"Error deleting book: {e}")
        return templates.TemplateResponse("admin_dashboard.html", {
            "request": request,
            "message": f"Failed to delete book: {e}"
        })


@app.post("/delete-book/{book_id}", response_class=HTMLResponse)
def delete_book(request: Request, book_id: int):
    username = request.session.get("user")
    if not username:
        return RedirectResponse(url="/login", status_code=302)

    try:
        # Delete the book from the database
        cursor.execute("""
            DELETE FROM books
            WHERE book_id = %s AND user_id = (SELECT user_id FROM users WHERE username = %s)
        """, (book_id, username))
        conn.commit()
        return RedirectResponse(url="/?message=Book deleted successfully!", status_code=302)
    except Exception as e:
        conn.rollback()
        return RedirectResponse(url=f"/?message=Failed to delete book: {e}", status_code=302)

@app.get("/wishlist", response_class=HTMLResponse)
def view_wishlist(request: Request):
    username = request.session.get("user")
    if not username:
        return RedirectResponse(url="/login", status_code=302)

    # Fetch the user's wishlist items
    cursor.execute("""
        SELECT b.title, b.author, b.genre, b.description, b.cover_image, b.book_id
        FROM wishlist w
        JOIN books b ON w.book_id = b.book_id
        JOIN users u ON w.user_id = u.user_id
        WHERE u.username = %s
    """, (username,))
    wishlist_books = cursor.fetchall()

    return templates.TemplateResponse("wishlist.html", {
        "request": request,
        "books": wishlist_books,
        "username": username
    })


@app.post("/wishlist/add/{book_id}", response_class=HTMLResponse)
def add_to_wishlist(request: Request, book_id: int):
    username = request.session.get("user")
    if not username:
        return RedirectResponse(url="/login", status_code=302)

    # Get the user's ID
    cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    user_id = user[0]

    try:
        # Add the book to the user's wishlist
        cursor.execute("INSERT INTO wishlist (user_id, book_id) VALUES (%s, %s)", (user_id, book_id))
        conn.commit()
        return RedirectResponse(url=f"/book/{book_id}?message=Added to wishlist!", status_code=302)
    except psycopg2.IntegrityError:
        conn.rollback()
        return RedirectResponse(url=f"/book/{book_id}?message=Book already in wishlist!", status_code=302)
    except Exception as e:
        conn.rollback()
        print(f"Error adding to wishlist: {e}")
        return RedirectResponse(url=f"/book/{book_id}?message=Failed to add to wishlist.", status_code=302)


@app.post("/wishlist/remove/{book_id}", response_class=HTMLResponse)
def remove_from_wishlist(request: Request, book_id: int):
    username = request.session.get("user")
    if not username:
        return RedirectResponse(url="/login", status_code=302)

    # Get the user's ID
    cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    user_id = user[0]

    try:
        # Remove the book from the user's wishlist
        cursor.execute("DELETE FROM wishlist WHERE user_id = %s AND book_id = %s", (user_id, book_id))
        conn.commit()
        return RedirectResponse(url="/wishlist", status_code=302)
    except Exception as e:
        conn.rollback()
        return templates.TemplateResponse("wishlist.html", {
            "request": request,
            "message": f"Failed to remove book from wishlist: {e}"
        })


@app.post("/admin/delete-review/{review_id}", response_class=HTMLResponse)
def delete_review(request: Request, review_id: int):
    try:
        cursor.execute("DELETE FROM reviews WHERE review_id = %s", (review_id,))
        conn.commit()
        return RedirectResponse(url="/admin", status_code=302)
    except Exception as e:
        conn.rollback()
        return templates.TemplateResponse("admin_dashboard.html", {
            "request": request,
            "message": f"Failed to delete review: {e}"
        })

@app.get("/sell-book", response_class=HTMLResponse)
def sell_book_get(request: Request):
    username = request.session.get("user")
    if not username:
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("sell_book.html", {"request": request})


@app.post("/sell-book", response_class=HTMLResponse)
async def sell_book_post(
    request: Request,
    title: str = Form(...),
    author: str = Form(...),
    genre: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),  # New field for price
    cover_image: UploadFile = File(...)
):
    username = request.session.get("user")
    if not username:
        return RedirectResponse(url="/login", status_code=302)

    # Get the user's ID
    cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    user_id = user[0]

    # Save the uploaded cover image
    file_location = UPLOAD_DIR / cover_image.filename
    with open(file_location, "wb") as f:
        shutil.copyfileobj(cover_image.file, f)

    try:
        # Insert the book into the database
        cursor.execute("""
            INSERT INTO books (user_id, title, author, genre, description, price, cover_image, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, NOW())
        """, (user_id, title, author, genre, description, price, f"books/{cover_image.filename}"))
        conn.commit()
        return templates.TemplateResponse("sell_book.html", {
            "request": request,
            "message": "Book added successfully!"
        })
    except Exception as e:
        conn.rollback()
        return templates.TemplateResponse("sell_book.html", {
            "request": request,
            "message": f"Failed to add book: {e}"
        })

@app.get("/admin-dashboard", response_class=HTMLResponse)
def admin_dashboard(request: Request):
    user = request.session.get("user")
    if user != "admin":
        return RedirectResponse(url="/admin-login", status_code=302)

    # Fetch all users
    try:
        cursor.execute("""
            SELECT user_id, username, email, created_at  FROM users 
            ORDER BY user_id ASC 
        """)
        users = cursor.fetchall()
    except Exception as e:
        users = []
        print(f"Error fetching users: {e}")

    # Fetch all books
    try:
        cursor.execute("""
            SELECT book_id, title, author, genre, condition
            FROM books
            ORDER BY created_at DESC
        """)
        books = cursor.fetchall()
    except Exception as e:
        books = []
        print(f"Error fetching books: {e}")

    # Fetch all transactions
    try:
        cursor.execute("""
            SELECT transaction_id, status, transaction_date, book_id
            FROM transactions
            ORDER BY transaction_date DESC
        """)
        transactions = cursor.fetchall()
    except Exception as e:
        transactions = []
        print(f"Error fetching transactions: {e}")

    # Fetch all reviews
    try:
        cursor.execute("""
            SELECT review_id, book_id, rating, comment, created_at
            FROM reviews
            ORDER BY created_at DESC
        """)
        reviews = cursor.fetchall()
    except Exception as e:
        reviews = []
        print(f"Error fetching reviews: {e}")

    # Pass the data to the template
    return templates.TemplateResponse("admin_dashboard.html", {
        "request": request,
        "users": users,
        "books": books,
        "transactions": transactions,
        "reviews": reviews
    })



@app.get("/admin/delete-book/{book_id}")
def delete_book(book_id: int):
    cursor.execute("DELETE FROM books WHERE id = %s", (book_id,))
    conn.commit()
    return RedirectResponse(url="/admin-dashboard", status_code=302)


@app.get("/admin/delete-review/{review_id}")
def delete_review(review_id: int):
    cursor.execute("DELETE FROM reviews WHERE id = %s", (review_id,))
    conn.commit()
    return RedirectResponse(url="/admin-dashboard", status_code=302)

@app.get("/admin/add-book", response_class=HTMLResponse)
def admin_add_book(request: Request):
    user = request.session.get("user")
    if user != "admin":
        return RedirectResponse(url="/admin-login", status_code=302)
    return templates.TemplateResponse("admin_add_book.html", {"request": request})


@app.post("/admin/add-book", response_class=HTMLResponse)
async def admin_add_book_post(request: Request, title: str = Form(...), author: str = Form(...), genre: str = Form(...), description: str = Form(...), cover_image: UploadFile = File(...)):
    file_location = UPLOAD_DIR / cover_image.filename
    with open(file_location, "wb") as f:
        shutil.copyfileobj(cover_image.file, f)

    cursor.execute("""
        INSERT INTO books (title, author, genre, description, cover_image, created_at)
        VALUES (%s, %s, %s, %s, %s, NOW())
    """, (title, author, genre, description, f"books/{cover_image.filename}"))
    conn.commit()
    return RedirectResponse(url="/admin-dashboard", status_code=302)


@app.get("/admin/edit-book/{book_id}", response_class=HTMLResponse)
def admin_edit_book(request: Request, book_id: int):
    user = request.session.get("user")
    if user != "admin":
        return RedirectResponse(url="/admin-login", status_code=302)

    cursor.execute("SELECT book_id, title, author, genre, description FROM books WHERE book_id = %s", (book_id,))
    book = cursor.fetchone()
    return templates.TemplateResponse("admin_edit_book.html", {"request": request, "book": book})


@app.post("/admin/edit-book/{book_id}", response_class=HTMLResponse)
async def admin_edit_book_post(request: Request, book_id: int, title: str = Form(...), author: str = Form(...), genre: str = Form(...), description: str = Form(...)):
    cursor.execute("""
        UPDATE books
        SET title = %s, author = %s, genre = %s, description = %s
        WHERE book_id = %s
    """, (title, author, genre, description, book_id))
    conn.commit()
    return RedirectResponse(url="/admin-dashboard", status_code=302)


@app.get("/admin/delete-book/{book_id}")
def admin_delete_book(book_id: int):
    cursor.execute("DELETE FROM books WHERE book_id = %s", (book_id,))
    conn.commit()
    return RedirectResponse(url="/admin-dashboard", status_code=302)

@app.get("/reviews", response_class=HTMLResponse)
def write_review(request: Request):
    username = request.session.get("user")
    if not username:
        return RedirectResponse(url="/login", status_code=302)

    cursor.execute("""
        SELECT b.title, b.author, b.book_id
        FROM transactions t
        JOIN books b ON t.book_id = b.book_id
        JOIN users u ON t.buyer_id = u.user_id
        WHERE u.username = %s AND t.status = 'Completed'
    """, (username,))
    books = cursor.fetchall()

    return templates.TemplateResponse("reviews.html", {"request": request, "books": books})


@app.post("/reviews/submit", response_class=HTMLResponse)
def submit_review(request: Request, book_id: int = Form(...), rating: int = Form(...), comment: str = Form(None)):
    username = request.session.get("user")
    if not username:
        return RedirectResponse(url="/login", status_code=302)

    cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
    user_id = cursor.fetchone()[0]

    try:
        cursor.execute("""
            INSERT INTO reviews (user_id, book_id, rating, comment, created_at)
            VALUES (%s, %s, %s, %s, NOW())
        """, (user_id, book_id, rating, comment))
        conn.commit()
        return RedirectResponse(url="/", status_code=302)
    except Exception as e:
        conn.rollback()
        return templates.TemplateResponse("reviews.html", {"request": request, "message": f"Failed to submit review: {e}"})


@app.get("/search", response_class=HTMLResponse)
def search_books(request: Request, query: str = Query(None), genre: str = Query(None), condition: str = Query(None), trade_option: bool = Query(None), rating: int = Query(None)):
    filters = []
    params = []

    if query:
        filters.append("(title ILIKE %s OR author ILIKE %s)")
        params.extend([f"%{query}%", f"%{query}%"])
    if genre:
        filters.append("genre = %s")
        params.append(genre)
    if condition:
        filters.append("condition = %s")
        params.append(condition)
    if trade_option is not None:
        filters.append("trade_option = %s")
        params.append(trade_option)
    if rating:
        filters.append("book_id IN (SELECT book_id FROM reviews WHERE rating >= %s)")
        params.append(rating)

    where_clause = " AND ".join(filters)
    query = f"SELECT title, author, genre, condition, cover_image, book_id FROM books"
    if where_clause:
        query += f" WHERE {where_clause}"
    query += " ORDER BY created_at DESC"

    cursor.execute(query, tuple(params))
    books = cursor.fetchall()

    return templates.TemplateResponse("search.html", {"request": request, "books": books})

@app.post("/admin/delete-user/{user_id}", response_class=HTMLResponse)
def delete_user(request: Request, user_id: int):
    user = request.session.get("user")
    if user != "admin":
        return RedirectResponse(url="/admin-login", status_code=302)

    try:
        cursor.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        conn.commit()
        return RedirectResponse(url="/admin", status_code=302)
    except Exception as e:
        conn.rollback()
        print(f"Error deleting user: {e}")
        return templates.TemplateResponse("admin_dashboard.html", {
            "request": request,
            "message": f"Failed to delete user: {e}"
        })

@app.post("/buy/{book_id}", response_class=HTMLResponse)
def buy_book(request: Request, book_id: int):
    username = request.session.get("user")
    if not username:
        return RedirectResponse(url="/login", status_code=302)

    # Get the user's ID
    cursor.execute("SELECT user_id FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    buyer_id = user[0]

    # Get the seller ID and price of the book
    cursor.execute("SELECT user_id, price, title FROM books WHERE book_id = %s", (book_id,))
    book = cursor.fetchone()
    if not book:
        return RedirectResponse(url="/", status_code=302)

    seller_id, price, title = book

    try:
        # Record the transaction
        cursor.execute("""
            INSERT INTO transactions (buyer_id, seller_id, book_id, transaction_type, status, transaction_date)
            VALUES (%s, %s, %s, 'Sell', 'Completed', NOW())
        """, (buyer_id, seller_id, book_id))
        conn.commit()
        return RedirectResponse(url="/?message=Successfully purchased the book!", status_code=302)
    except Exception as e:
        conn.rollback()
        return RedirectResponse(url=f"/?message=Failed to complete purchase: {e}", status_code=302)

@app.get("/transactions", response_class=HTMLResponse)
def view_transactions(request: Request):
    username = request.session.get("user")
    if not username:
        return RedirectResponse(url="/login", status_code=302)

    # Fetch the user's transactions
    cursor.execute("""
        SELECT t.transaction_id, b.title AS book_title, b.price, t.transaction_date, t.status
        FROM transactions t
        JOIN books b ON t.book_id = b.book_id
        JOIN users u ON t.buyer_id = u.user_id
        WHERE u.username = %s
        ORDER BY t.transaction_date DESC
    """, (username,))
    transactions = cursor.fetchall()

    return templates.TemplateResponse("transactions.html", {
        "request": request,
        "transactions": transactions
    })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

