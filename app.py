from flask import Flask, render_template, request, redirect, url_for,flash,session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,SelectField
from wtforms.validators import DataRequired, Length, EqualTo,Optional

import requests

app = Flask(__name__)




#the form validation and storing 
app.config['SECRET_KEY'] = 'mysecretkey'

# PostgreSQL configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    type=db.Column(db.String(80),nullable=False)
    password = db.Column(db.String(120), nullable=False)

# Form for user registration
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    type =   SelectField(
        "User",
        choices=["Admin","Other"],
        validators=[DataRequired()]
    )
    submit = SubmitField('Register')

# Form for user login
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    type =   SelectField(
        "User",
        choices=["Admin","Other"],
        validators=[DataRequired()],
    )
    submit = SubmitField('Login')

# class Book(db.Model):
#     id = db.Column(db.Integer, primary_key=True)
#     title =  db.Column(db.String(100), nullable=False)
#     authors = db.Column(db.String(100), nullable=False)
#     description = db.Column(db.String(100), nullable=False)
#     poster=description = db.Column(db.String(100), nullable=False)


class Book1(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    authors=db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    price=db.Column(db.String(100),nullable=False)

class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(120), nullable=False)

with app.app_context():
    db.create_all()


# Admin side
@app.route('/')
@app.route('/home')
def home():
    form = LoginForm() 
    return render_template('home.html', form=form)

@app.route('/Admin_home')
def Admin_home():
    return render_template("Admin.html")

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()  # Initialize registration form
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('Username already exists, please choose a different one.')
            return redirect(url_for('register'))

        # Create new user entry
        new_user = User(username=form.username.data, password=form.password.data,type=form.type.data)
        db.session.add(new_user)
        db.session.commit()
        if form.type.data=="Admin":
            new_user = Admin(username=form.username.data, password=form.password.data)
            db.session.add(new_user)
            db.session.commit()
        flash('Registration successful! You can now log in.')
        session["user_name"] = form.username.data
        next_url = request.args.get("next")
        return redirect(next_url or url_for("home"))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data, password=form.password.data,type=form.type.data).first()
        user1 = Admin.query.filter_by(username=form.username.data, password=form.password.data).first()
        if user or user1:
            if form.type.data=="Other":
                flash('Login successful!')
                session["user_name"] = form.username.data
                next_url = request.args.get("next")
                return redirect(next_url or url_for("home"))
            else : 
                return redirect(url_for("Admin_home"))
        else:
            flash('Login failed. Check your username and password.')
    return render_template('login.html', form=form)


@app.route("/resp")
def resp():
    k=[]
    books = Book1.query.all()
    for i in books:
        k.append(i.name)
    
    book_data = []
    return render_template("resp.html",books=books)

@app.route('/books')
def view_books():
    # Fetch all books from the database
    books = Book1.query.all()
    return render_template('Adimin_ADD.html', books=books)

@app.route("/add_Admin",methods=['POST'])
def Adimin_ADD(): 
     book_name = request.form['book_name']
     author_name=request.form['author_name']
     book_price=request.form['book_price']
     description=request.form['d']
     
     new_book = Book1(name=book_name,authors=author_name,description=description,price=book_price)
    # Add and commit the new book to the database
     db.session.add(new_book)
     db.session.commit()
     return redirect(url_for('view_books'))

@app.route("/add_member")
def add_member(): 
    member=Admin.query.all()
    return  render_template("Adimin_member.html",member=member)


@app.route("/add_mem",methods=['POST'])
def Adimin(): 
     name = request.form['username']
     password=request.form['password']
     
     new_book = Admin(username=name,password=password)
    # Add and commit the new book to the database
     db.session.add(new_book)
     db.session.commit()
     return redirect(url_for('add_member'))


@app.route('/delete/<int:member_id>')
def Delete_member(member_id):
    # Get the book by ID from the database
    book_to_delete = Admin.query.get_or_404(member_id)
    db.session.delete(book_to_delete)
    db.session.commit()

    return redirect(url_for('add_member'))

@app.route('/delete1/<int:book_id>')
def Delete_BOOK(book_id):
    # Get the book by ID from the database
    book_to_delete = Book1.query.get_or_404(book_id)

    # Delete the book
    db.session.delete(book_to_delete)
    db.session.commit()

    return redirect(url_for('view_books'))

@app.route('/check', methods=['GET'])
def check_book():
    # Redirect to view books when "Check" is clicked
    return redirect(url_for('view_books'))
#Userside code
# Google Books API endpoint
GOOGLE_BOOKS_API_URL = "https://www.googleapis.com/books/v1/volumes"

@app.route("/index", methods=["GET", "POST"])
def home1():
    if 'user_name' not in session:
        return redirect(url_for('login', next=request.url))
    books = None
    if request.method == "POST":
        query = request.form.get("query")
        params = {
            "q": query,
            "maxResults": 10 
        }
        response = requests.get(GOOGLE_BOOKS_API_URL, params=params)
        if response.status_code == 200:
            data = response.json()
            books = []
            for item in data.get("items", []):
                book_info = item["volumeInfo"]
                book_id = item["id"]
                title = book_info.get("title", "N/A")
                poster = book_info.get("imageLinks", {}).get("thumbnail", "#")
                price = "N/A"
                sale_info = item.get("saleInfo", {})
                if sale_info.get("saleability") == "FOR_SALE":
                    price = sale_info.get("retailPrice", {}).get("amount", "N/A")
                books.append({"id": book_id, "title": title, "poster": poster, "price": price})
    return render_template("index.html", books=books)

@app.route("/book/<book_id>")
def book_detail(book_id):
    # Fetch book details using book ID
    response = requests.get(f"{GOOGLE_BOOKS_API_URL}/{book_id}")
    if response.status_code == 200:
        book = response.json()
        title = book["volumeInfo"].get("title", "N/A")
        authors = book["volumeInfo"].get("authors", [])
        description = book["volumeInfo"].get("description", "No description available")
        poster = book["volumeInfo"].get("imageLinks", {}).get("thumbnail", "#")
        sale_info = book.get("saleInfo", {})
        price = sale_info.get("retailPrice", {}).get("amount", "N/A")
        buy_link = sale_info.get("buyLink", "#")

        
        return render_template("book_detail.html", title=title, authors=authors, description=description, poster=poster, price=price, buy_link=buy_link)
    return redirect(url_for("index"))


@app.route("/Top_books",methods=["GET", "POST"])
def Top_book():
    if 'user_name' not in session:
        return redirect(url_for('login', next=request.url))
    k=[]
    books = Book1.query.all()
    for i in books:
        k.append(i.name)
    
    book_data = []
    return render_template("Top.html",books=books)



class User_BOOK(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    book_name = db.Column(db.String(120), nullable=False)
    book_author=db.Column(db.String(120),nullable=False)



@app.route("/added")
def added(): 
    if 'user_name' not in session:
        return redirect(url_for('login', next=request.url))
    user_book=User_BOOK.query.all()
    return  render_template("added.html",books=user_book)

#      return redirect(url_for('add_member'))


@app.route('/book_details1/<int:book_id>')
def book_details1(book_id):
    # Query the database for the specific book by its ID
    book = Book1.query.get_or_404(book_id)
    name=session['user_name']
    book_name=book.name
    book_author=book.authors
    new_book = User_BOOK(username=name,book_name=book_name,book_author=book_author)
    db.session.add(new_book)
    db.session.commit()
    return redirect(url_for("Top_book"))




@app.route('/delete12/<int:book_id>')
def Delete_book2(book_id):
    # Get the book by ID from the database
    book_to_delete = User_BOOK.query.get_or_404(book_id)
    # Delete the book
    db.session.delete(book_to_delete)
    db.session.commit()
    return redirect(url_for('added'))



with app.app_context():
    db.create_all()



if __name__ == "__main__":
    app.run(debug=True)
