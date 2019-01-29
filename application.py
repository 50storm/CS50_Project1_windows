import os

from flask import Flask, session, render_template, request, Response, flash, redirect
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from models import *
import datetime, sys, re
from jinja2 import evalcontextfilter, Markup, escape

_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

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

@app.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') \
        for p in _paragraph_re.split(escape(value)))
    if eval_ctx.autoescape:
        result = Markup(result)
    return result

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
    user = users.fetchone()
    if(user == None):
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
    sqlUser = "SELECT * FROM users WHERE username=:username AND password=:password"
    
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()
        user = db.execute(
            sqlUser,
            {"username":username,"password":password}
        )
        rowUser = user.fetchone()
        if(rowUser is None):
            return render_template("index.html", message="Login Error...Incorrect passward entered.. Please Try agin.")
        
        print(username)
        print(password)
        print(rowUser)
        session['username'] = rowUser['username']
        session['password'] = rowUser['password']
      
        return render_template("mypage.html", username=rowUser["username"], message="")
   
    #GET
    return render_template("mypage.html", username=session.get("username") ,  message="")

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
    #book
    isbn =""
    title=""
    author=""
    year=""

    username=""
    rate=-1
    comment=""
    sql_book = "SELECT * FROM books WHERE isbn=:isbn "
    sql_my_book_review = "SELECT  u.username as username, br.rate as rate, br.comment as comment, br.isbn as isbn FROM bookreviews br INNER JOIN users u ON br.user_id = u.id WHERE isbn=:isbn AND user_id = :user_id "
    sql_book_reiviews =  "SELECT  u.username as username, br.rate as rate, br.comment as comment, br.isbn as isbn FROM bookreviews br INNER JOIN users u ON br.user_id = u.id WHERE isbn=:isbn "
    if request.method == "GET":
        isbn   = request.args.get("isbn","")
        user_id =  session.get("user_id")
        
        print("==debug==")
        print(isbn)#None
        book = db.execute(
            sql_book,
            {"isbn":isbn}
        )
        row_book = book.fetchone()
        if(row_book is not None):
            #表示用
            isbn   = row_book["isbn"]
            author = row_book["author"]
            title  = row_book["title"]
            year   = row_book["year"]
    
            #Sessionに持っておく(1レコード分)
            session["isbn"]   = row_book["isbn"]
            session["author"] = row_book["author"]
            session["title"]  = row_book["title"]
            session["year"]   = row_book["year"]
    
        
        mybookreview = db.execute(
            sql_my_book_review,
            {"isbn":isbn,"user_id":user_id}
        )
        row_mybookreview = mybookreview.fetchone()
        if(row_mybookreview is not None) :
            username = row_mybookreview['username']
            rate = row_mybookreview['rate']
            comment = row_mybookreview['comment']

        bookreviews = db.execute(
            sql_book_reiviews,
            {"isbn":isbn }
        )
        return render_template("bookdetail.html", isbn=isbn, title=title, author=author, year=year, rate = rate, comment=comment, bookreviews=bookreviews )

@app.route("/writeBookReview", methods=["GET","POST"])
def writeBookReview():
    if request.method == "POST":#TODO
        rate = request.form.get("rate").strip()
        comment = request.form.get("comment").strip()
        user_id = session.get("user_id")
        isbn    = session.get("isbn")
        title   = session.get("title")
        author  = session.get("author")
        year    = session.get("year")
 
  
        insertSQL ="INSERT INTO bookreviews (isbn, user_id, rate, comment, created_at ) VALUES (:isbn, :user_id, :rate, :comment, current_timestamp)" #TODO;isbn
        params    = {"isbn":isbn, "user_id":user_id, "rate":rate ,"comment":comment }
        
        resultInsert = db.execute(insertSQL, params)
        db.commit()
        
        return render_template("bookdetail.html", isbn=isbn, title=title, author=author, year=year )

@app.route("/updateBookReview", methods=["GET","POST"])
def updateBookReview():
    if request.method == "POST":#TODO
        rate = request.form.get("rate").strip()
        comment = request.form.get("comment").strip()
        user_id = session.get("user_id")
        isbn    = session.get("isbn")
        title   = session.get("title")
        author  = session.get("author")
        year    = session.get("year")
 
  
        updateSQL ="UPDATE bookreviews  SET  rate = :rate, comment = :comment, created_at=current_timestamp  WHERE isbn = :isbn AND user_id = :user_id "
        params    = {"isbn":isbn, "user_id":user_id, "rate":rate, "comment":comment }
        
        resultInsert = db.execute(updateSQL, params)
        db.commit()
        
        return render_template("bookdetail.html", isbn=isbn, title=title, author=author, year=year , comment=comment )

@app.route("/deleteBookReview", methods=["GET","POST"])
def deleteBookReview():
    if request.method == "POST":#TODO
        # rate = request.form.get("rate").strip()
        # comment = request.form.get("comment").strip()
        user_id = session.get("user_id")
        isbn    = session.get("isbn")
        title   = session.get("title")
        author  = session.get("author")
        year    = session.get("year")
 
 
        updateSQL ="DELETE FROM  bookreviews  WHERE isbn = :isbn AND user_id = :user_id "
        params    = {"isbn":isbn, "user_id":user_id  }
        
        resultInsert = db.execute(updateSQL, params)
        db.commit()
        
        return render_template("bookdetail.html", isbn=isbn, title=title, author=author, year=year , comment="" )

        
@app.route("/getsession")
def getsession():
    session.pop("username", None)

    if 'username' in session:
        #return session['username']
        return session.get("username")

    return "Not Loggin"
