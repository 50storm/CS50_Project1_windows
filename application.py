import os

from flask import Flask, session, render_template, request, Response, flash, redirect, jsonify, url_for, abort
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import datetime, sys, re
from jinja2 import evalcontextfilter, Markup, escape
from flask_sqlalchemy import SQLAlchemy 


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

#Create SQLAlchemy Instance
db = SQLAlchemy()
db.init_app(app)
#Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.errorhandler(500)
def internal_error(e):
    print(e)
    flash("Sorry Error occured.." , "alert alert-danger")
    flash(str(e), "alert alert-danger")
    return render_template("error.html"), 500

@app.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
    _paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

    # print(eval_ctx)
    print(value)
    # result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') for p in _paragraph_re.split(escape(value)))
    result = u'\n\n'.join(u'%s<br>' % p.replace('\n', '<br>') for p  in _paragraph_re.split(escape(value)))
 
    if eval_ctx.autoescape:
        result = Markup(result)
    return result

def isLoggedin():
    app.logger.debug('=====isLoggedin====')
    app.logger.debug(session.get('user_id'))
    if( session.get('user_id') == "" ) :
        print("session expired.")
        return False
    else:
        return True

def checkPassword(password, confiromPassword, username, user_id=None, for_update=False):
    if(not for_update):
        if(len(password) < 7):
            return (False, "password is too short!")
        elif(password in username):
            return (False, "password is in username!!")
        elif(password != confiromPassword):
            return (False, "password is not equal confiromPassword!!")
        else:
            return (True, None)
    else:
        users = db.execute(
            "SELECT * FROM users WHERE user_id=:user_id AND password=:password",
            {"user_id": user_id, "password": password}
        )
        user = users.fetchone()
        if(user == None):
            return (False, "password is not equal to registered password!")
        else:
            return (True, None)

def checkUserName(username, user_id=None, for_update=False):
    if( username == "" ):
        return (False, "Plsease enter username.")
    result_execute = db.execute( "SELECT * FROM users WHERE username=:username",{"username":username} )
    user = result_execute.fetchone()
    if(user == None):
        return (True, None)
    else:
        if(for_update==False):
            if(username == user['username']):
                return (False, username + " is alreaded used.")
            else:
                return (True, None)
        else:
            if(user_id == user['user_id']):
                return (True, None)
            elif(username == user['username']):
                return (False, username + " is alreaded used.")
            else:
                return (True, None)
        
def find_book_by_isbn(isbn):
    book = db.execute("SELECT * FROM books WHERE isbn=:isbn ", {"isbn":isbn})
    return  book.fetchone()

def find_my_book_review(isbn, user_id):
    #None or Dictionary  dic["rate"]
    sql_my_book_review = "SELECT u.username as username, br.rate as rate, br.comment as comment, br.isbn as isbn FROM bookreviews br "
    sql_my_book_review += "INNER JOIN users u ON br.user_id = u.user_id  "
    sql_my_book_review +=  " WHERE br.isbn=:isbn AND u.user_id = :user_id"
    mybookreview = db.execute( sql_my_book_review, {"isbn":isbn,"user_id":user_id} )
    row_mybookreview = mybookreview.fetchone() #only one record
    if(row_mybookreview is None) :
        return None
    else:
        return row_mybookreview

def find_my_book_reviews(user_id):
    sql_my_book_reviews =   "SELECT br.created_at, u.username, br.rate, br.comment, br.isbn, b.title, b.author, b.year FROM bookreviews br "
    sql_my_book_reviews +=  " INNER JOIN users u ON br.user_id = u.user_id  "
    sql_my_book_reviews +=  " INNER JOIN books b ON b.isbn = br.isbn  "
    sql_my_book_reviews +=  " WHERE u.user_id = :user_id"
    mybookreview = db.execute( sql_my_book_reviews, { "user_id":user_id } )
    return mybookreview.fetchall()
    
def find_recent_book_reviews():
    sql_book_reiviews =   "SELECT br.created_at, u.username, br.rate, br.comment, br.isbn, b.title, b.author, b.year  FROM bookreviews br "
    sql_book_reiviews +=  " INNER JOIN users u ON br.user_id = u.user_id  "
    sql_book_reiviews +=  " INNER JOIN books b ON b.isbn = br.isbn  "
    sql_book_reiviews +=  " ORDER BY br.created_at DESC OFFSET 0 LIMIT 5"
    bookreviews = db.execute(sql_book_reiviews)
    return bookreviews.fetchall()

def find_book_reviews( isbn=None, user_id=None  ):
    #List [] list[0][0]
    print("==========find_book_reviews==========")
    sql_paramters ={}
    sql_book_reiviews =  "SELECT br.created_at, u.username as username, br.rate as rate, br.comment as comment, br.isbn as isbn FROM bookreviews br "
    sql_book_reiviews += " INNER JOIN users u ON br.user_id = u.user_id  "
    if(isbn is not None or user_id is not None):
        sql_book_reiviews +=  "  WHERE  "
        if(isbn is not None and user_id is not None):
            sql_book_reiviews += " isbn=:isbn AND user_id = :user_id"
            sql_paramters = {"isbn":isbn, "user_id":user_id }
        elif(isbn is not None and user_id is None):
            sql_book_reiviews += " isbn=:isbn "
            sql_paramters = {"isbn":isbn}
        elif(isbn is None and user_id is not None):
            sql_book_reiviews += " user_id =: user_id "
            sql_paramters = {"user_id": user_id}

    bookreviews = db.execute( sql_book_reiviews, sql_paramters )
    return bookreviews.fetchall() # [] = zeros

def setUserSession(user):
    session['user_id'] = user['user_id']
    session['username'] = user['username']
    session['firstname']= user['firstname']
    session['lastname'] = user['lastname']
    session['password'] = user['password'] 
    return
   
def unsetUserSession():
    session.pop("user_id", None)
    session.pop("username", None)
    session.pop("firstname", None)
    session.pop("lastname", None)
    session.pop("password", None)
    return

def setUserViewData(user_id='', username='', firstname='', lastname='', passsword=''):
    userdata={}
    userdata['user_id'] = user_id
    userdata['username'] = username
    userdata['firstname'] = firstname
    userdata['lastname'] = lastname
    userdata['password'] = passsword
    return userdata

@app.route("/api/<string:isbn>", methods=["GET"])
def api(isbn):
    book_info =  {
            "title": "",
            "author": "",
            "year":0 ,
            "isbn": "",
            "review_count": 0,
            "average_score": 0.0
            }
    if request.method == "GET":
        sqlSel = " SELECT b.title, b.author, b.year, b.isbn, count(*) as review_count , AVG(rate) as average_score "
        sqlSel += " FROM bookreviews br "
        sqlSel += " INNER JOIN books b "
        sqlSel += " ON br.isbn = b.isbn "
        sqlSel += " GROUP BY b.title, b.author, b.year, b.isbn "
        sqlSel += " HAVING  b.isbn = :isbn "
        book = db.execute(sqlSel, {"isbn":isbn})
        row_book = book.fetchone()
        if(row_book is None):
            return None
        else:
            book_info["title"] = row_book['title']
            book_info["author"] = row_book['author']
            book_info["year"] = row_book['year']
            book_info["isbn"] = row_book['isbn']
            book_info["review_count"] = row_book['review_count']
            print(row_book['average_score'])
            book_info["average_score"] = round(float(row_book['average_score']),1)
            return jsonify(book_info)

@app.route("/", methods=["GET"])
def root():
    return render_template("index.html")

@app.route("/login", methods=["GET"])
def login():
    return render_template("index.html")

@app.route("/login", methods=["POST"])
def validate_login():
    try:
        sqlUser = "SELECT * FROM users WHERE username=:username AND password=:password"
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()
        user = db.execute(
            sqlUser,
            {"username":username,"password":password}
        )
        rowUser = user.fetchone()
        
        if(rowUser is None):
            session['username'] = username
            return render_template("index.html", message="Login Error...Incorrect passward entered.. Please Try agin.")

        setUserSession(rowUser)
        app.logger.info('%s logged in successfully', rowUser.username)
    except Exception as e :
        print(str(e)) #TODO error log
        # http://k-kuro.hatenadiary.jp/entry/20180119/p1
        # https://www.hiramine.com/physicalcomputing/raspberrypi3/flask_debug.html
        # http://flask.pocoo.org/docs/1.0/logging/
        # https://codehandbook.org/writing-error-log-in-python-flask-web-application/
        abort( 500, "Login Page" )
    
    return redirect(url_for("mypage"))

@app.route("/registerUser", methods=["GET","POST"])
def registerUser():
    try:
        if request.method == "POST":
            confirmPassword = request.form.get("confirmPassword").strip()
            userdata = setUserViewData("", 
                            request.form.get("username").strip(), 
                            request.form.get("firstname").strip(),
                            request.form.get("lastname").strip(),
                            request.form.get("password").strip())

            resultCheckUserName = checkUserName(userdata['username'])
            resultCheckPassword = checkPassword(userdata['password'], confirmPassword, userdata['username'])
            print(resultCheckUserName)
            print(resultCheckPassword)
            if(resultCheckUserName[0] and resultCheckPassword[0]):
                print("======userdata========")
                print(userdata)
                return render_template("registration.html", userdata=userdata, mode=1)
            else:
                #invalid inputs
                # messages=[1]
                messages=["",""] #String Message
                category=["",""] #CSS Class
                if( resultCheckUserName[0] == False ):
                    #http://flask.pocoo.org/docs/1.0/patterns/flashing/
                    messages[0] = resultCheckUserName[1]
                    category[0] = 'text-danger'
                    flash(messages[0], category[0])
                if( resultCheckPassword[0]  == False ):
                    messages[1] = resultCheckPassword[1]
                    category[1] = 'text-danger '
                    flash(messages[1], category[1])
                return render_template("registration.html", userdata=userdata, mode=0)
        else:  # GET
            return render_template("registration.html",userdata=setUserViewData("","","","",""),mode=0)
    except Exception as e :
         print(str(e)) #TODO error log
         abort( 500, "registerUser" )
     
@app.route("/confirmUser", methods=["POST"])
def confirmUser():
    try:
        userdata = setUserViewData("", 
                            request.form.get("username").strip(), 
                            request.form.get("firstname").strip(),
                            request.form.get("lastname").strip(),
                            request.form.get("password").strip())
        return render_template("registration.html", userdata=userdata, mode=2)
    except Exception as e :
         print(str(e)) #TODO error log
         abort(500, "confirmUser")
    
@app.route("/insertUser", methods=["POST"])
def insertUser():
    try:
        userdata = setUserViewData("", 
                            request.form.get("username").strip(), 
                            request.form.get("firstname").strip(),
                            request.form.get("lastname").strip(),
                            request.form.get("password").strip())
        print("====userdata===")
        print(userdata)
        insertSQL ="INSERT INTO users (username, firstname, lastname, password, created_at )VALUES (:username, :firstname, :lastname, :password, current_timestamp)"
        params    = {"username":userdata['username'], "firstname":userdata['firstname'], "lastname":userdata['lastname'], "password":userdata['password']}
        resultInsert = db.execute(insertSQL, params)
        db.commit()
        print("====registered====")
        flash("Successfully Registed!＼(^o^)／ Thank you!", "alert alert-success")
        return render_template("registration.html", userdata=userdata, mode=3)
    except Exception as e:
         print(str(e))  # TODO error log
         abort(500, "confirmUser")

@app.route("/mypage", methods=["GET"])
def mypage():
    try:
        #GET ONLY
        if(not isLoggedin):
            return redirect(url_for("error"))

        recent_book_reviews = find_recent_book_reviews()
        my_book_reviews = find_my_book_reviews(session.get("user_id"))
        print(my_book_reviews)
        return render_template("mypage.html", username=session.get("username") , recent_book_reviews=recent_book_reviews, my_book_reviews=my_book_reviews)
    except Exception as e:
         print(str(e))  # TODO error log
         abort(500, "confirmUser")

@app.route("/showUserAccount", methods=["GET"])
def showUserAccount():
    try:
        #GET ONLY
        if(not isLoggedin):
            #TODO:Error Message by flashing
            return redirect(url_for("error"))
        userdata = setUserViewData(session['user_id'], session['username'], session['firstname'], session['lastname'], session['password'])
        print(userdata)
        return render_template("user_account.html", userdata=userdata, mode=0)
    except Exception as e:
         print(str(e))  # TODO error log
         abort(500, "confirmUser")

@app.route("/editUserAccount", methods=["GET"])
def editUserAccount():
    try:
        if(not isLoggedin):
            #TODO:Error Message by flashing
            return redirect(url_for("error"))
        userdata = setUserViewData(session['user_id'], session['username'],session['firstname'], session['lastname'], session['password'])
        return render_template("user_account.html", userdata=userdata, mode=1)
    except Exception as e:
         print(str(e))  # TODO error log
         abort(500, "confirmUser")

@app.route("/updateUserAccount", methods=["POST"])
def updateUserAccount():
    try:
        if(not isLoggedin):
            #TODO:Error Message by flashing
            return redirect(url_for("error"))
        userdata = setUserViewData(session['user_id'],
                                   request.form.get("username").strip(),
                                   request.form.get("firstname").strip(), 
                                   request.form.get("lastname").strip(),
                                   request.form.get("password").strip())
        updateSQL ="UPDATE  users SET username=:username, firstname=:firstname, lastname=:lastname, created_at=current_timestamp "
        updateSQL += "WHERE user_id = :user_id "
        params = {"user_id":session['user_id'], "username": userdata['username'], "firstname": userdata['firstname'], "lastname": userdata['lastname'] }
        resultInsert = db.execute(updateSQL, params)
        db.commit()
        setUserSession(userdata)
        flash("Successfully Updated!＼(^o^)／ Thank you!", "alert alert-success")
        return render_template("user_account.html", userdata=userdata, mode=3)
    except Exception as e:
         print(str(e))  # TODO error log
         abort(500, "confirmUser")

@app.route("/confirmUserAccount", methods=["POST"])
def confirmUserAccount():
    try:
        if(not isLoggedin):
            #TODO:Error Message by flashing
            return redirect(url_for("error"))
        if request.method == "POST":
            userdata = setUserViewData(session['user_id'],
                                       request.form.get("username").strip(),
                                       request.form.get("firstname").strip(), 
                                       request.form.get("lastname").strip(),
                                       request.form.get("password").strip()
                                       )
            print("===========userdata==============")
            print(userdata)
    
            resultCheckUserName = checkUserName(userdata['username'], session['user_id'], True)
            resultCheckPassword = checkPassword( userdata['password'], None, None, session['user_id'],True)
    
            if(resultCheckUserName[0] and resultCheckPassword[0]):
                return render_template("user_account.html", userdata=userdata, mode=2)
            else:  # invalid data
                messages=["",""] #String Message
                category=["",""] #CSS Class
                if( resultCheckUserName[0] == False ):
                    #http://flask.pocoo.org/docs/1.0/patterns/flashing/
                    messages[0] = resultCheckUserName[1]
                    category[0] = 'text-danger alert alert-danger'
                    flash(messages[0], category[0])
                if( resultCheckPassword[0]  == False ):
                    messages[1] = resultCheckPassword[1]
                    category[1] = 'text-danger alert alert-danger'
                    flash(messages[1], category[1])
                return render_template("user_account.html", userdata=userdata, mode=1)
    except Exception as e:
         print(str(e))  # TODO error log
         abort(500, "confirmUser")

@app.route("/logout", methods=["POST"])
def logout():
    try:
        unsetUserSession()
        return render_template("logout.html")
    except Exception as e:
        print(str(e))  # TODO error log
        abort(500, "logout")

@app.route("/search", methods=["GET"])
def search():
    try:
        #GET ONLY
        if(not isLoggedin):
            return redirect(url_for("error"))
        recent_book_reviews = find_recent_book_reviews()
        my_book_reviews = find_my_book_reviews(session.get("user_id"))
        print(my_book_reviews)
        return render_template("search.html", username=session.get("username") , recent_book_reviews=recent_book_reviews, my_book_reviews=my_book_reviews)
    except Exception as e:
        print(str(e))  # TODO error log
        abort(500, "search")

@app.route("/searchBooks", methods=["GET"])
def searchBooks():
    try:
        if(not isLoggedin):
            return redirect(url_for("error"))
        booktitle  = '%' + request.args.get("booktitle").strip() + '%'
        isbn       = '%' + request.args.get("isbn").strip() + '%'
        authorname = '%' + request.args.get("authorname").strip() + '%'

        if ( booktitle == "" and isbn == "" and authorname == "" ):
            print("error")

        queryBookBase = "SELECT * FROM books "
        queryBookWhere =""
        sqlparameters ={}

        if ( booktitle != "%%" and isbn != "%%" and authorname != "%%"):
            queryBookWhere += " WHERE "
            queryBookWhere += " title LIKE :title "
            queryBookWhere += " AND isbn LIKE  :isbn "
            queryBookWhere += " AND author LIKE :author "
            sqlparameters = {"title":booktitle, "isbn":isbn, "author":authorname }
        elif( booktitle != "%%" and isbn != "%%" and authorname == "%%"):
            queryBookWhere += " WHERE "
            queryBookWhere += " title LIKE :title "
            queryBookWhere += " AND isbn LIKE :isbn "
            sqlparameters = {"title":booktitle, "isbn":isbn }

        elif( booktitle != "%%" and isbn == "%%" and authorname != "%%"):
            queryBookWhere += " WHERE "
            queryBookWhere += " title LIKE :title "
            queryBookWhere += " AND author LIKE :author "
            sqlparameters = {"title":booktitle, "author":authorname }

        elif( booktitle == "%%" and isbn != "%%" and authorname != "%%"):
            queryBookWhere += " WHERE "
            queryBookWhere += " isbn LIKE :isbn "
            queryBookWhere += " AND author LIKE :author "
            sqlparameters = {"isbn":isbn, "author":authorname }

        elif( booktitle != "%%" and isbn == "%%" and authorname == "%%" ):
            queryBookWhere += " WHERE "
            queryBookWhere += " title LIKE :title "
            sqlparameters = {"title":booktitle }

        elif( booktitle == "%%" and isbn != "%%" and authorname == "%%"):
            queryBookWhere += " WHERE "
            queryBookWhere += " isbn LIKE :isbn "
            sqlparameters = {"isbn":isbn }

        elif( booktitle == "%%" and isbn == "%%" and authorname != "%%"):
            queryBookWhere += " WHERE "
            queryBookWhere += " author LIKE :author "
            sqlparameters = {"author":authorname }

        else:
            print("raise error")

        queryBook = queryBookBase + queryBookWhere
        print("====queryBook======")
        print(queryBook)
        print("====sqlparameters===")
        print(sqlparameters)

        books = db.execute(queryBook,sqlparameters)
        booklist = books.fetchall()
        return render_template("booklist.html", books= booklist)
    except Exception as e:
        print(str(e))  # TODO error log
        abort(500, "searchBooks")


@app.route("/searchBook", methods=["GET"])
def searchBook():
    try:
        if(not isLoggedin):
            return redirect(url_for("error"))
        isbn   = request.args.get("isbn","")
        user_id =  session.get("user_id")
        bookinfo = find_book_by_isbn(isbn)

        mybookreview = find_my_book_review(isbn, user_id)
        bookreviews = find_book_reviews(isbn)

        return render_template("bookdetail.html", bookinfo=bookinfo, bookreviews=bookreviews, mybookreview=mybookreview )
    except Exception as e:
        print(str(e))  # TODO error log
        abort(500, "searchBook")


@app.route("/registerSubmission", methods=["GET"])
def registerSubmission():
    try:
        if(not isLoggedin):
            return redirect(url_for("error"))
        isbn   = request.args.get("isbn","")
        bookinfo = find_book_by_isbn(isbn)
        return render_template("register_submission.html", bookinfo=bookinfo )
    except Exception as e:
        print(str(e))  # TODO error log
        abort(500, "registerSubmission")
        
@app.route("/writeBookReview", methods=["POST"])
def writeBookReview():
    try:
        if(not isLoggedin):
            return redirect(url_for("error"))
        rate    = request.form.get("rate").strip()
        comment = request.form.get("comment").strip()
        user_id = session.get("user_id")
        isbn    = request.form.get("isbn")
       
        insertSQL ="INSERT INTO bookreviews (isbn, user_id, rate, comment, created_at ) VALUES (:isbn, :user_id, :rate, :comment, current_timestamp)"
        params    = {"isbn":isbn, "user_id":user_id, "rate":rate ,"comment":comment }

        db.execute(insertSQL, params)
        db.commit()
        mybookreview = find_my_book_review(isbn, user_id)
        bookinfo = find_book_by_isbn(isbn)
        
        flash("Successfully Posted!＼(^o^)／ Thank you!", "alert alert-success")
        return render_template("register_submission.html", bookinfo=bookinfo, mybookreview=mybookreview, rate=rate, comment=comment, is_confirmation=True, is_posted=True )
    except Exception as e:
        print(str(e))  # TODO error log
        abort(500, "writeBookReview")

@app.route("/confirmYourEntry", methods=["POST"])
def confirmYourEntry():
    try:
        if(not isLoggedin):
            return redirect(url_for("error"))
        rate    = request.form.get("rate").strip()
        comment = request.form.get("comment").strip()
        user_id = session.get("user_id")
        isbn    = request.form.get("isbn")
        # for update
        mybookreview = find_my_book_review(isbn, user_id)
        bookinfo = find_book_by_isbn(isbn)
        if(comment.strip() == ""):
            flash('Your review is empty!! Please write your review', 'alert alert-danger')
            return render_template("register_submission.html", bookinfo=bookinfo, mybookreview=mybookreview, rate=rate, comment=comment,  is_confirmation=False )
        return render_template("register_submission.html", bookinfo=bookinfo, mybookreview=mybookreview, rate=rate, comment=comment,  is_confirmation=True )

    except Exception as e:
        print(str(e))  # TODO error log
        abort(500, "confirmYourEntry")

@app.route("/editSubmission", methods=["GET"])
def editSubmission():
    try:
        if(not isLoggedin):
            return redirect(url_for("error"))
        user_id = session.get("user_id")
        isbn   = request.args.get("isbn","")
        mybookreview = find_my_book_review(isbn, user_id)
        bookinfo = find_book_by_isbn(isbn)
        return render_template("edit_submission.html", bookinfo=bookinfo, mybookreview=mybookreview )
    except Exception as e:
        print(str(e))  # TODO error log
        abort(500, "editSubmission")

@app.route("/confirmEditEntry", methods=["POST"])
def confirmEditEntry():
    try:
        if(not isLoggedin):
            return redirect(url_for("error"))
        rate    = request.form.get("rate").strip()
        comment = request.form.get("comment").strip()
        isbn    = request.form.get("isbn")
        bookinfo = find_book_by_isbn(isbn)
        if(comment.strip() == ""):
            flash('Your review is empty!! Please write your review', 'alert alert-danger')
            return render_template("edit_submission.html", bookinfo=bookinfo, mybookreview=None, rate=rate, comment=comment,  is_confirmation=False )
        return render_template("edit_submission.html", bookinfo=bookinfo, mybookreview=None, rate=rate, comment=comment,  is_confirmation=True )
    except Exception as e:
        print(str(e))  # TODO error log
        abort(500, "confirmYourEntry")

@app.route("/updateBookReview", methods=["POST"])
def updateBookReview():
    try:
        if(not isLoggedin):
            return redirect(url_for("error"))
        rate = request.form.get("rate").strip()
        comment = request.form.get("comment").strip()
        user_id = session.get("user_id")
        isbn    = request.form.get("isbn")

        updateSQL ="UPDATE bookreviews  SET  rate = :rate, comment = :comment, created_at=current_timestamp  WHERE isbn = :isbn AND user_id = :user_id "
        params    = {"isbn":isbn, "user_id":user_id, "rate":rate, "comment":comment }

        db.execute(updateSQL, params)
        db.commit()

        # for display
        mybookreview = find_my_book_review(isbn, user_id)
        bookinfo = find_book_by_isbn(isbn)
        flash("Successfully Updated!＼(^o^)／ Thank you!", "alert alert-success")
        return render_template("edit_submission.html", bookinfo=bookinfo, mybookreview=mybookreview, rate=rate, comment=comment, is_confirmation=True, is_posted=True )
    except Exception as e:
        print(str(e))  # TODO error log
        abort(500, "updateBookReview")

@app.route("/deleteBookReview", methods=["POST"])
def deleteBookReview():
    try:
        if(not isLoggedin):
            return redirect(url_for("error"))
        user_id = session.get("user_id")
        isbn    = request.form.get("isbn")

        deleteSQL ="DELETE FROM  bookreviews  WHERE isbn = :isbn AND user_id = :user_id "
        params    = {"isbn":isbn, "user_id":user_id  }

        db.execute(deleteSQL, params)
        db.commit()
        bookinfo = find_book_by_isbn(isbn)
        
        flash("Successfully Deleted!＼(^o^)／ Thank you!", "alert alert-success")
        return render_template("delete_submission.html", bookinfo=bookinfo, mybookreview=None )
    except Exception as e:
        print(str(e))  # TODO error log
        abort(500, "deleteBookReview")

@app.route("/error")
def error():
    return render_template("error.html")
