import os

from flask import Flask, session, render_template, request, Response, flash, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from models import *
import datetime, sys

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

#Add Igarashi
app.config["SQLALCHEMY_DATABASE_URI"]  = os.getenv("DATABASE_URL")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db.init_app(app)

Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def checkPassword( password, confiromPassword, username ):
    if( len(password) <7 ):
        return (False, "password is too short!")
    elif( password in username ):
        return (False, "password is in username!!")
    elif( password != confiromPassword):
        return (False, "password is not equal confiromPassword!!")
    else:
        return (True, None)

def checkUserName(username):
    if( username == "" ):
        return (False, "Plsease enter username.")
    users = db.execute(
        "SELECT * FROM users WHERE username=:username",
        {"username":username}
    )
    usersList = users.fetchall()
    print("======debug=============")
    print(usersList) #list
    for user in usersList:
        print(user["username"])

    if(len(usersList) == 0):
        return (True, None)
    else:
        return (False, username + " is alreaded used.")

@app.route("/", methods=["GET"])
def root():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("index.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username").strip()
        firstname = request.form.get("firstname").strip()
        lastname = request.form.get("lastname").strip()
        password = request.form.get("password").strip()
        confirmPassword = request.form.get("confirmPassword").strip()

        resultCheckUserName = checkUserName(username)

        resultCheckPassword = checkPassword(password, confirmPassword, username)
        print(resultCheckUserName)
        print(resultCheckPassword)
        if(resultCheckUserName[0] and resultCheckPassword[0]):
            insertSQL ="INSERT INTO users (username, firstname, lastname, password, created_at )VALUES (:username, :firstname, :lastname, :password, current_timestamp)"
            params    = {"username":username, "firstname":firstname, "lastname":lastname, "password":password}
            resultInsert = db.execute(insertSQL, params)
            db.commit()
            print(resultInsert)
            return render_template("success.html")
        else:
            #invalid inputs
            # messages=[1]
            messages=["",""]
            category=["",""]
            if( resultCheckUserName[0] == False ):
                #http://flask.pocoo.org/docs/1.0/patterns/flashing/
                messages[0] = resultCheckUserName[1]
                category[0] = 'text-danger'
                flash(messages[0], category[0])
            if( resultCheckPassword[0]  == False ):
                messages[1] = resultCheckPassword[1]
                category[1] = 'text-danger'
                flash(messages[1], category[1])
            return render_template("registration.html")

    #GET
    return render_template("registration.html")

@app.route("/mypage", methods=["GET", "POST"])
def mypage():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()
        print(username)
        print(password)
        users = db.execute(
            "SELECT * FROM users WHERE username=:username AND password=:password",
            {"username":username, "password":password}
        )
        # Add data to Seession
        for user in users :
            session["user_id"]=user["id"]
			
        session["username"] = username
        session["password"] = password

        return render_template("mypage.html", users=users)
    #GET
    print("====GET[Session]=====")
    username = session.get("username")
    password = session.get("password")
    print(username)
    print(password)
    users = db.execute(
        "SELECT * FROM users WHERE username=:username AND password=:password",
        {"username":username, "password":password}
    )
    return render_template("mypage.html", users=users)

@app.route("/logout", methods=["POST"])
def logout():
    if request.method == "POST":
        session.pop("username", None)
        session.pop("password", None)
        return render_template("logout.html")

@app.route("/searchBooks", methods=["GET","POST"])
def searchBooks():
    if request.method == "POST":
        booktitle  = '%' + request.form.get("booktitle").strip() + '%'
        isbn       = request.form.get("isbn").strip()
        authorname = request.form.get("authorname").strip()

        if ( booktitle == "" and isbn == "" and authorname == "" ):
            print("error")

        queryBookBase = "SELECT * FROM books "
        queryBookWhere =""
        sqlparameters ={}

        if ( booktitle != "" and isbn != "" and authorname != ""):
            queryBookWhere += " WHERE "
            queryBookWhere += " title like ':title' "
            queryBookWhere += " AND isbn =:isbn "
            queryBookWhere += " AND author =:author "
            sqlparameters = {"title":booktitle, "isbn":isbn, "author":authorname }
        elif( booktitle != "" and isbn != "" and authorname == ""):
            queryBookWhere += " WHERE "
            queryBookWhere += " title like :title "
            queryBookWhere += " AND isbn =:isbn "
            sqlparameters = {"title":booktitle, "isbn":isbn }

        elif( booktitle != "" and isbn == "" and authorname != ""):
            queryBookWhere += " WHERE "
            queryBookWhere += " title like :title "
            queryBookWhere += " AND author =:author "
            sqlparameters = {"title":booktitle, "author":authorname }

        elif( booktitle == "" and isbn != "" and authorname != ""):
            queryBookWhere += " WHERE "
            queryBookWhere += " isbn =:isbn "
            queryBookWhere += " AND author =:author "
            sqlparameters = {"isbn":isbn, "author":authorname }

        elif( booktitle != "" and isbn == "" and authorname == "" ):
            queryBookWhere += " WHERE "
            queryBookWhere += " title like :title "
            sqlparameters = {"title":booktitle }

        elif( booktitle == "" and isbn != "" and authorname == ""):
            queryBookWhere += " WHERE "
            queryBookWhere += " isbn =:isbn "
            sqlparameters = {"isbn":isbn }

        elif( booktitle == "" and isbn == "" and authorname != ""):
            queryBookWhere += " WHERE "
            queryBookWhere += " author =:author "
            sqlparameters = {"author":authorname }

        else:
            print("raise error")

        queryBook = queryBookBase + queryBookWhere
        print("====queryBook===")
        print(queryBook)
        print("====sqlparameters===")
        print(sqlparameters)

        books = db.execute(queryBook,sqlparameters)
        # booklist = books.fetchall()
        # for book in booklist:
        #     session["isbn"]  = book["isbn"]
        #     session["title"] =  book["isbn"]
        #     session["author"] =  book["author"]

        return render_template("booklist.html", books=books)

    return render_template("mypage.html")

@app.route("/searchBook", methods=["GET","POST"])
def searchBook():
    title=""
    author=""
    year=""
    isbn = request.args.get("isbn","")
    print("==debug==")
    print(isbn)#None
    book = db.execute(
        "SELECT * FROM books WHERE isbn=:isbn",
        {"isbn":isbn}
    )
    for b in book:
        print(b["isbn"])
        print(b["title"])
        print(b["author"])
        print(b["year"])
        #Sessionに持っておく(1レコード分)
        session["isbn"] = b["isbn"]
        session["author"] = b["author"]
        session["title"] = b["title"]
        session["year"] = b["year"]
  
        #表示用
        author = b["author"]
        title = b["title"]
        year = b["year"]
        
        
        
    print("========")
    print(author)

    return render_template("bookdetail.html", isbn=isbn, title=title, author=author, year=year )

@app.route("/writeBookReview", methods=["GET","POST"])
def writeBookReview():
    if request.method == "POST":#TODO
        comment = request.form.get("comment").strip()
        user_id = session.get("user_id")
        isbn    = session.get("isbn")
        title   = session.get("title")
        author  = session.get("author")
        year    = session.get("year")
        
        insertSQL ="INSERT INTO bookreviews (isbn, user_id, comment, created_at ) VALUES (:isbn, :user_id, :comment, current_timestamp)" #TODO;isbn
        params    = {"isbn":isbn, "user_id":user_id, "comment":comment }
        
        resultInsert = db.execute(insertSQL, params)
        db.commit()
        
        return render_template("bookdetail.html", isbn=isbn, title=title, author=author, year=year )

@app.route("/getsession")
def getsession():
    session.pop("username", None)

    if 'username' in session:
        #return session['username']
        return session.get("username")

    return "Not Loggin"
