import os, datetime, sys, re, logging

from flask import Flask, session, render_template, request, Response, flash, redirect, jsonify, url_for, abort
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from jinja2 import evalcontextfilter, Markup, escape
from logging.config import dictConfig
from flask_cors import CORS  # pip install Flask-Cors


dictConfig({
    'version': 1,
    'formatters': {
        'file': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'file',
            'filename': './log/bookrevie_app.log',
            'backupCount': 3,
            'when': 'D',
        }
    },
    'root': {
        'level': 'DEBUG',
        'handlers': ['file']
    }
})

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

# Set Flask-Cors
CORS(app)

PREFIX="/bookreivew"

@app.errorhandler(500)
def internal_error(e):
    app.logger.debug(e)
    flash("Sorry Error occured.." , "alert alert-danger")
    flash(str(e), "alert alert-danger")
    return render_template("error.html"), 500

@app.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
    _paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')

    # app.logger.debug(eval_ctx)
    app.logger.debug(value)
    # result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') for p in _paragraph_re.split(escape(value)))
    result = u'\n\n'.join(u'%s<br>' % p.replace('\n', '<br>') for p  in _paragraph_re.split(escape(value)))
 
    if eval_ctx.autoescape:
        result = Markup(result)
    return result

def isLoggedin():
    app.logger.debug('=====isLoggedin====')
    app.logger.debug(session.get('user_id'))
    print(session.get('user_id'))
    if( session.get('user_id') is None ) :
        app.logger.debug("")
        flash('session expired.', 'alert alert-danger')
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
        users.close()
        db.close()
        if(user == None):
            return (False, "password is not equal to registered password!")
        else:
            return (True, None)

def checkUserName(username, user_id=None, for_update=False):
    if( username == "" ):
        return (False, "Plsease enter username.")
    result_execute = db.execute( "SELECT * FROM users WHERE username=:username",{"username":username} )
    user = result_execute.fetchone()
    result_execute.close()
    db.close()
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
    result = None
    book = db.execute("SELECT * FROM books WHERE isbn=:isbn ", {"isbn":isbn})
    result = book.fetchone()
    book.close()
    db.close()
    return  result

def find_my_book_review(isbn, user_id):
    result = None
    sql_my_book_review = "SELECT u.username as username, br.rate as rate, br.comment as comment, br.isbn as isbn FROM bookreviews br "
    sql_my_book_review += "INNER JOIN users u ON br.user_id = u.user_id  "
    sql_my_book_review +=  " WHERE br.isbn=:isbn AND u.user_id = :user_id"
    mybookreview = db.execute( sql_my_book_review, {"isbn":isbn,"user_id":user_id} )
    row_mybookreview = mybookreview.fetchone() #only one record
    mybookreview.close()
    db.close()
    if(row_mybookreview is None) :
        return None
    else:
        return row_mybookreview

def find_my_book_reviews(user_id):
    result = []
    sql_my_book_reviews =   "SELECT br.created_at, u.username, br.rate, br.comment, br.isbn, b.title, b.author, b.year FROM bookreviews br "
    sql_my_book_reviews +=  " INNER JOIN users u ON br.user_id = u.user_id  "
    sql_my_book_reviews +=  " INNER JOIN books b ON b.isbn = br.isbn  "
    sql_my_book_reviews +=  " WHERE u.user_id = :user_id"
    mybookreview = db.execute( sql_my_book_reviews, { "user_id":user_id } )
    result = mybookreview.fetchall()
    mybookreview.close()
    db.close()
    return  result
    
def find_recent_book_reviews():
    result = []
    sql_book_reiviews =   "SELECT br.created_at, u.username, br.rate, br.comment, br.isbn, b.title, b.author, b.year  FROM bookreviews br "
    sql_book_reiviews +=  " INNER JOIN users u ON br.user_id = u.user_id  "
    sql_book_reiviews +=  " INNER JOIN books b ON b.isbn = br.isbn  "
    # sql_book_reiviews +=  " ORDER BY br.created_at DESC OFFSET 0 LIMIT 5"
    sql_book_reiviews +=  " ORDER BY br.created_at DESC "
    bookreviews = db.execute(sql_book_reiviews)
    result = bookreviews.fetchall() 
    bookreviews.close()
    db.close()
    return result

def find_book_reviews( isbn=None, user_id=None ):
    result = []
    app.logger.debug("==========find_book_reviews==========")
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
    result = bookreviews.fetchall() # [] = zeros
    db.close()
    return result

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

#http://localhost:5000/bookreivew/api/0061150142
@app.route(PREFIX + "/api/<string:isbn>", methods=["GET"])
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
        book.close()
        db.close()
        # app.logger.debug(book)
        if(row_book is None):
            return jsonify(row_book)
        else:
            book_info["title"] = row_book['title']
            book_info["author"] = row_book['author']
            book_info["year"] = row_book['year']
            book_info["isbn"] = row_book['isbn']
            book_info["review_count"] = row_book['review_count']
            app.logger.debug(row_book['average_score'])
            book_info["average_score"] = round(float(row_book['average_score']),1)
            return jsonify(book_info)

#http://localhost:5000/bookreivew/api/getBookReviewNumber/1
@app.route(PREFIX + "/api/getBookReviewNumber/<string:user_id>", methods=["GET"])
def get_book_review_number(user_id):
    book_info = {
        "username":"" ,
        "review_count": 0,
    }
    if request.method == "GET":
        sqlSel = " SELECT u.username, count(*) as review_count , AVG(rate) as average_score "
        sqlSel += " FROM bookreviews br "
        sqlSel += " INNER JOIN books b "
        sqlSel += " ON br.isbn = b.isbn "
        sqlSel += " INNER JOIN users u "
        sqlSel += " ON u.user_id = br.user_id "
        sqlSel += " GROUP BY u.user_id "
        sqlSel += " HAVING  u.user_id = :user_id "
        app.logger.debug(sqlSel)
        book = db.execute(sqlSel, {"user_id": user_id})
        row_book = book.fetchone()
        book.close()
        db.close()
        # app.logger.debug(book)
        if(row_book is None):
            return jsonify(row_book)
        else:
            book_info["username"] = row_book['username']
            book_info["review_count"] = row_book['review_count']

            return jsonify(book_info)

# TODO 途中セーブ
def get_goodreaders_review(isbn):
    result ={'work_ratings_count':0,
             'work_text_reviews_count':0,
             'average_rating':''
            }
    print(isbn)
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "TTCvwkSmt1K5rBsTszGg", "isbns": isbn})
    print(res)
    json_str = res.json()
    work_ratings_count = json_str['books'][0]['work_ratings_count']
    print( work_ratings_count )
    work_text_reviews_count = json_str['books'][0]['work_text_reviews_count']
    print( work_text_reviews_count )
    average_rating = json_str['books'][0]['work_text_reviews_count']
    print( average_rating )
    result['work_ratings_count'] = work_ratings_count
    result['work_text_reviews_count'] = work_text_reviews_count
    result['average_rating'] = average_rating
    print(result)

    return result

@app.route(PREFIX + "/charttest/", methods=["GET"])
def charttest():
    return render_template("charttest.html")

@app.route(PREFIX + "/apitest/", methods=["GET"])
def apitest():
    return render_template("apitest.html")

@app.route("/", methods=["GET"])
def root():
    return redirect(url_for("login"))

@app.route(PREFIX + "/",  methods=["GET"])
def prefix_root():
    return redirect(url_for("login"))

@app.route(PREFIX + "/login", methods=["GET"])
def login():
    return render_template("index.html")


@app.route(PREFIX + "/login", methods=["POST"])
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
        user.close()
        db.close()
        if(rowUser is None):
            session['username'] = username
            return render_template("index.html", message="Login Error...Incorrect passward entered.. Please Try agin.")

        setUserSession(rowUser)
        app.logger.info('%s logged in successfully', rowUser.username)
    except Exception as e :
        app.logger.error(str(e))
        abort( 500, "Login Page" )
    
    return redirect(url_for("mypage"))


@app.route(PREFIX + "/registerUser", methods=["GET", "POST"])
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
            app.logger.debug(resultCheckUserName)
            app.logger.debug(resultCheckPassword)
            if(resultCheckUserName[0] and resultCheckPassword[0]):
                # Validation is fine!
                flash("Please confirm your input data", "alert alert-info")
                app.logger.debug("======userdata========")
                app.logger.debug(userdata)

                return render_template("registration.html", userdata=userdata, mode=1)
            else:
                #s Validtation is invalid...
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
         app.logger.error(str(e))
         abort( 500, "registerUser" )
     


@app.route(PREFIX + "/insertUser", methods=["POST"])
def insertUser():
    try:
        userdata = setUserViewData("", 
                            request.form.get("username").strip(), 
                            request.form.get("firstname").strip(),
                            request.form.get("lastname").strip(),
                            request.form.get("password").strip())
        app.logger.debug("====userdata===")
        app.logger.debug(userdata)
        insertSQL ="INSERT INTO users (username, firstname, lastname, password, created_at )VALUES (:username, :firstname, :lastname, :password, current_timestamp)"
        params    = {"username":userdata['username'], "firstname":userdata['firstname'], "lastname":userdata['lastname'], "password":userdata['password']}
        resultInsert = db.execute(insertSQL, params)
        db.commit()
        db.close()
        app.logger.debug("====registered====")
        flash("Successfully Registed!＼(^o^)／ Thank you!", "alert alert-success")
        return render_template("registration.html", userdata=userdata, mode=2)
    except Exception as e:
         app.logger.error(str(e))   
         abort(500, "confirmUser")


@app.route(PREFIX + "/mypage", methods=["GET"])
def mypage():
    try:
        #GET ONLY
        if(not isLoggedin()):
            return redirect(url_for("error"))

        recent_book_reviews = find_recent_book_reviews()
        my_book_reviews = find_my_book_reviews(session.get("user_id"))
        app.logger.debug(my_book_reviews)
        return render_template("mypage.html", username=session.get("username") , recent_book_reviews=recent_book_reviews, my_book_reviews=my_book_reviews)
    except Exception as e:
         app.logger.error(str(e))   
         abort(500, "confirmUser")


@app.route(PREFIX + "/showUserAccount", methods=["GET"])
def showUserAccount():
    try:
        #GET ONLY
        if(not isLoggedin()):
            return redirect(url_for("error"))
        userdata = setUserViewData(session['user_id'], session['username'], session['firstname'], session['lastname'], session['password'])
        app.logger.debug(userdata)
        return render_template("user_account.html", userdata=userdata, mode=0)
    except Exception as e:
         app.logger.error(str(e))   
         abort(500, "confirmUser")


@app.route(PREFIX + "/editUserAccount", methods=["GET"])
def editUserAccount():
    try:
        if(not isLoggedin()):
            return redirect(url_for("error"))
        userdata = setUserViewData(session['user_id'], session['username'],session['firstname'], session['lastname'], session['password'])
        return render_template("user_account.html", userdata=userdata, mode=1)
    except Exception as e:
         app.logger.error(str(e))   
         abort(500, "confirmUser")


@app.route(PREFIX + "/confirmUserAccount", methods=["POST"])
def confirmUserAccount():
    try:
        if(not isLoggedin()):
            return redirect(url_for("error"))
        if request.method == "POST":
            userdata = setUserViewData(session['user_id'],
                                       request.form.get("username").strip(),
                                       request.form.get("firstname").strip(), 
                                       request.form.get("lastname").strip(),
                                       request.form.get("password").strip()
                                       )
            app.logger.debug("===========userdata==============")
            app.logger.debug(userdata)
    
            resultCheckUserName = checkUserName(userdata['username'], session['user_id'], True)
            resultCheckPassword = checkPassword( userdata['password'], None, None, session['user_id'],True)
    
            if(resultCheckUserName[0] and resultCheckPassword[0]):
                # Validation is true
                flash("Please confirm your input data", "alert alert-info")
                return render_template("user_account.html", userdata=userdata, mode=2)
            else:  
                # Validation is false
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
         app.logger.error(str(e))   
         abort(500, "confirmUser")


@app.route(PREFIX + "/updateUserAccount", methods=["POST"])
def updateUserAccount():
    try:
        if(not isLoggedin()):
            return redirect(url_for("error"))
        userdata = setUserViewData(session['user_id'],
                                   request.form.get("username").strip(),
                                   request.form.get("firstname").strip(), 
                                   request.form.get("lastname").strip(),
                                   request.form.get("password").strip())
        updateSQL ="UPDATE  users SET username=:username, firstname=:firstname, lastname=:lastname, updated_at=current_timestamp "
        updateSQL += "WHERE user_id = :user_id "
        params = {"user_id":session['user_id'], "username": userdata['username'], "firstname": userdata['firstname'], "lastname": userdata['lastname'] }
        resultInsert = db.execute(updateSQL, params)
        db.commit()
        db.close()
        setUserSession(userdata)
        flash("Successfully Updated!＼(^o^)／ Thank you!", "alert alert-success")
        return render_template("user_account.html", userdata=userdata, mode=3)
    except Exception as e:
         app.logger.error(str(e))   
         abort(500, "confirmUser")


@app.route(PREFIX + "/logout", methods=["POST"])
def logout():
    try:
        unsetUserSession()
        db.close()
        return render_template("logout.html")
    except Exception as e:
        app.logger.error(str(e))   
        abort(500, "logout")


@app.route(PREFIX + "/search", methods=["GET"])
def search():
    try:
        #GET ONLY
        if(not isLoggedin()):
            return redirect(url_for("error"))
        recent_book_reviews = find_recent_book_reviews()
        my_book_reviews = find_my_book_reviews(session.get("user_id"))
        app.logger.debug(my_book_reviews)
        return render_template("search.html", username=session.get("username") , recent_book_reviews=recent_book_reviews, my_book_reviews=my_book_reviews)
    except Exception as e:
        app.logger.error(str(e))   
        abort(500, "search")


@app.route(PREFIX + "/searchBooks", methods=["GET"])
def searchBooks():
    try:
        if(not isLoggedin()):
            return redirect(url_for("error"))
        booktitle  = '%' + request.args.get("booktitle").strip() + '%'
        isbn       = '%' + request.args.get("isbn").strip() + '%'
        authorname = '%' + request.args.get("authorname").strip() + '%'

        if ( booktitle == "" and isbn == "" and authorname == "" ):
            app.logger.debug("error")

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
            app.logger.debug("raise error")

        queryBook = queryBookBase + queryBookWhere
        app.logger.debug("====queryBook======")
        app.logger.debug(queryBook)
        app.logger.debug("====sqlparameters===")
        app.logger.debug(sqlparameters)

        books = db.execute(queryBook,sqlparameters)
        booklist = books.fetchall()
        books.close()
        db.close()
        return render_template("booklist.html", books= booklist)
    except Exception as e:
        app.logger.error(str(e))
        abort(500, "searchBooks")


@app.route(PREFIX + "/searchBook", methods=["GET"])
def searchBook():
    try:
        if(not isLoggedin()):
            return redirect(url_for("error"))
        isbn   = request.args.get("isbn","")
        user_id =  session.get("user_id")
        bookinfo = find_book_by_isbn(isbn)

        mybookreview = find_my_book_review(isbn, user_id)
        bookreviews = find_book_reviews(isbn)

        return render_template("bookdetail.html", bookinfo=bookinfo, bookreviews=bookreviews, mybookreview=mybookreview )
    except Exception as e:
        app.logger.error(str(e))   
        abort(500, "searchBook")


@app.route(PREFIX + "/registerSubmission", methods=["GET"])
def registerSubmission():
    try:
        if(not isLoggedin()):
            return redirect(url_for("error"))
        isbn   = request.args.get("isbn","")
        bookinfo = find_book_by_isbn(isbn)
        return render_template("write_bookreview.html", bookinfo=bookinfo )
    except Exception as e:
        app.logger.error(str(e))   
        abort(500, "registerSubmission")
        

@app.route(PREFIX + "/writeBookReview", methods=["POST"])
def writeBookReview():
    try:
        if(not isLoggedin()):
            return redirect(url_for("error"))
        rate    = request.form.get("rate").strip()
        comment = request.form.get("comment").strip()
        user_id = session.get("user_id")
        isbn    = request.form.get("isbn")
       
        insertSQL ="INSERT INTO bookreviews (isbn, user_id, rate, comment, created_at ) VALUES (:isbn, :user_id, :rate, :comment, current_timestamp)"
        params    = {"isbn":isbn, "user_id":user_id, "rate":rate ,"comment":comment }

        db.execute(insertSQL, params)
        db.commit()
        db.close()
        mybookreview = find_my_book_review(isbn, user_id)
        bookinfo = find_book_by_isbn(isbn)
        
        flash("Successfully Posted!＼(^o^)／ Thank you!", "alert alert-success")
        return render_template("write_bookreview.html", bookinfo=bookinfo, mybookreview=mybookreview, rate=rate, comment=comment, is_confirmation=True, is_posted=True )
    except Exception as e:
        app.logger.error(str(e))
        abort(500, "writeBookReview")


@app.route(PREFIX + "/confirmYourEntry", methods=["POST"])
def confirmYourEntry():
    try:
        if(not isLoggedin()):
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
            return render_template("write_bookreview.html", bookinfo=bookinfo, mybookreview=mybookreview, rate=rate, comment=comment,  is_confirmation=False )
        flash("Please confirm your input data", "alert alert-info")
        return render_template("write_bookreview.html", bookinfo=bookinfo, mybookreview=mybookreview, rate=rate, comment=comment,  is_confirmation=True )

    except Exception as e:
        app.logger.error(str(e))
        abort(500, "confirmYourEntry")


@app.route(PREFIX + "/editSubmission", methods=["GET"])
def editSubmission():
    try:
        if(not isLoggedin()):
            return redirect(url_for("error"))
        user_id = session.get("user_id")
        isbn   = request.args.get("isbn","")
        mybookreview = find_my_book_review(isbn, user_id)
        bookinfo = find_book_by_isbn(isbn)
        return render_template("edit_bookreview.html", bookinfo=bookinfo, mybookreview=mybookreview )
    except Exception as e:
        app.logger.error(str(e)) 
        abort(500, "editSubmission")


@app.route(PREFIX + "/confirmEditEntry", methods=["POST"])
def confirmEditEntry():
    try:
        if(not isLoggedin()):
            return redirect(url_for("error"))
        rate    = request.form.get("rate").strip()
        comment = request.form.get("comment").strip()
        isbn    = request.form.get("isbn")
        bookinfo = find_book_by_isbn(isbn)
        if(comment.strip() == ""):
            flash('Your review is empty!! Please write your review', 'alert alert-danger')
            return render_template("edit_bookreview.html", bookinfo=bookinfo, mybookreview=None, rate=rate, comment=comment,  is_confirmation=False )
        flash("Please confirm your input data", "alert alert-info")
        return render_template("edit_bookreview.html", bookinfo=bookinfo, mybookreview=None, rate=rate, comment=comment,  is_confirmation=True )
    except Exception as e:
        app.logger.error(str(e))   
        abort(500, "confirmYourEntry")


@app.route(PREFIX + "/updateBookReview", methods=["POST"])
def updateBookReview():
    try:
        if(not isLoggedin()):
            return redirect(url_for("error"))
        rate = request.form.get("rate").strip()
        comment = request.form.get("comment").strip()
        user_id = session.get("user_id")
        isbn    = request.form.get("isbn")

        updateSQL ="UPDATE bookreviews  SET  rate = :rate, comment = :comment, updated_at=current_timestamp  WHERE isbn = :isbn AND user_id = :user_id "
        params    = {"isbn":isbn, "user_id":user_id, "rate":rate, "comment":comment }

        db.execute(updateSQL, params)
        db.commit()
        db.close()
        # for display
        mybookreview = find_my_book_review(isbn, user_id)
        bookinfo = find_book_by_isbn(isbn)
        flash("Successfully Updated!＼(^o^)／ Thank you!", "alert alert-success")
        return render_template("edit_bookreview.html", bookinfo=bookinfo, mybookreview=mybookreview, rate=rate, comment=comment, is_confirmation=True, is_posted=True )
    except Exception as e:
        app.logger.error(str(e))   
        abort(500, "updateBookReview")


@app.route(PREFIX + "/deleteBookReview", methods=["POST"])
def deleteBookReview():
    try:
        if(not isLoggedin()):
            return redirect(url_for("error"))
        user_id = session.get("user_id")
        isbn    = request.form.get("isbn")

        deleteSQL ="DELETE FROM  bookreviews  WHERE isbn = :isbn AND user_id = :user_id "
        params    = {"isbn":isbn, "user_id":user_id  }

        db.execute(deleteSQL, params)
        db.commit()
        db.close()
        bookinfo = find_book_by_isbn(isbn)
        
        flash("Successfully Deleted!＼(^o^)／ Thank you!", "alert alert-success")
        return render_template("delete_bookreview.html", bookinfo=bookinfo, mybookreview=None )
    except Exception as e:
        app.logger.error(str(e))   
        abort(500, "deleteBookReview")


@app.route(PREFIX + "/error")
def error():
    return render_template("error.html")
