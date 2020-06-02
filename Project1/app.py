import os
from flask import Flask, session, render_template, url_for, request, redirect, jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from Project1.goodreads import return_rating_by_isbn

app = Flask(__name__)
errors = []
# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.environ.get("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
@app.route("/home")
def home():
    print(session)
    return render_template("home.html")


def check_register(data):
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    confirm_password = data.get('confirm_password')
    if password != confirm_password:
        errors.append("Passwords don`t match")
        print("password")
        return False
    elif db.execute(f"SELECT * FROM \"Users\" WHERE username = :username", {"username": username}).fetchone():
        errors.append("User with this username has already exist. Choose another one.")
        print("username")
        return False
    elif db.execute(f"SELECT * FROM \"Users\" WHERE email = :email", {"email": email}).fetchone():
        errors.append("User with this email has already exist. Choose another one.")
        print("email")
        return False
    else:
        db.execute(f"INSERT INTO \"Users\" (username, email, password) VALUES (:username, :email, :password)",
                   {"username": username, "email": email, "password": password})
        db.commit()
        print("User has been added")
        return True


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        if check_register(request.form):
            return redirect(url_for("login"))
    return render_template("register.html", errors=errors)


def check_login(data):
    username = data.get('username')
    password = data.get('password')
    user = db.execute(f"SELECT * FROM \"Users\" WHERE username = :username", {"username": username}).fetchone()
    if user:
        if user.password == password:
            print("User has been logged")
            session['user_id'] = user.id
            return True, user
    print("User has NOT been logged")
    errors.append("Username or password are incorrect.")
    return False


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if check_login(request.form):
            return redirect(url_for("home"))
    return render_template("login.html", errors=errors)


@app.route("/loguot")
def logout():
    if not session.get('user_id'):
        return redirect('home')
    else:
        session.pop('user_id', None)
        return redirect('home')


@app.route("/search/", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        return redirect(url_for('search_item', result=request.form.get('search')))
    return render_template('search.html', errors=errors)


@app.route("/search/<string:result>", methods=["GET", "POST"])
def search_item(result):
    if request.method == "POST":
        return redirect(url_for('search_item', result=request.form.get('search')))
    search_results = db.execute(
        f"SELECT * FROM \"books\" WHERE isbn like '%{result}%' OR title like '%{result}%' OR author like '%{result}%' OR year like '%{result}%'").fetchall()
    return render_template('search.html', errors=errors, search_results=search_results)


@app.route("/book/<string:book_name>", methods=["GET", "POST"])
def book(book_name):
    book = db.execute(f"SELECT * FROM \"books\" WHERE title = '{book_name}'").fetchone()
    reviews = db.execute(
        r'SELECT username, rating, text FROM "Users" JOIN "reviews" ON "Users".id = reviews.user_id').fetchall()
    if request.method == "POST":
        user = db.execute(f"SELECT * FROM \"Users\" WHERE id = '{session.get('user_id')}'").fetchone()
        rating = request.form.get('rating')
        text = request.form.get('textarea')
        db.execute(f"INSERT INTO \"reviews\" (user_id, rating, text) VALUES (:user_id, :rating, :text)",
                   {"user_id": user.id, "rating": rating, "text": text})
        db.commit()
    return render_template('book.html', book=book, reviews=reviews, goodreads=return_rating_by_isbn(book.isbn))


@app.route("/isbn/<string:book_isbn>", methods=["GET", "POST"])
def isbn(book_isbn):
    book = db.execute(f"SELECT * FROM \"books\" WHERE isbn = '{book_isbn}'").fetchone()
    reviews = db.execute(
        r'SELECT username, rating, text FROM "Users" JOIN "reviews" ON "Users".id = "reviews".user_id').fetchall()
    if request.method == "POST":
        user = session.get('user_id')
        rating = request.form.get('rating')
        text = request.form.get('textarea')
        db.execute(f"INSERT INTO \"reviews\" (user_id, rating, text) VALUES (:user_id, :rating, :text)",
                   {"user_id": user.id, "rating": rating, "text": text})
        db.commit()
    return render_template('book.html', book=book, reviews=reviews, goodreads=return_rating_by_isbn(book.isbn))


@app.route("/author/<string:author_name>")
def author(author_name):
    authors_books = db.execute(f"SELECT * FROM \"books\" WHERE author = '{author_name}'").fetchall()
    return render_template('books.html', books=authors_books, title=author_name)


@app.route("/year/<string:y>")
def year(y):
    books_in_year = db.execute(f"SELECT * FROM \"books\" WHERE year = '{y}'").fetchall()
    return render_template('books.html', books=books_in_year, title=y)


@app.route("/api/<isbn>")
def api(isbn):
    book = db.execute(f"SELECT * FROM \"books\" WHERE isbn = '{isbn}'").fetchone()
    goodreads = return_rating_by_isbn(book.isbn)
    if book is None:
        return jsonify({"error": "Invalid isbn"}), 404
    else:
        return jsonify({"title": book.title, "author": book.author, "year": book.year, "isbn": book.isbn,
                        "review_count": goodreads['rating_count'], "average_score": goodreads['avg_rating']}), 200

if __name__ == '__main__':
    app.run(debug=True)
