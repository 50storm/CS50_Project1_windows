import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

conn = "postgres://hiroshi:Tera54hiro@localhost/bookreview"
engin = create_engine(conn)
db = scoped_session(sessionmaker(bind=engin))

def main():
    f = open("books.csv")
    reader = csv.reader(f)
    i=0;
    for isbn, title, author, year in reader:
        if (i!=0) :
            print(isbn)
            print(title)
            print(author)
            print(year)

            sqlInssert = "INSERT INTO books (isbn, title, author, year, created_at) VALUES( :isbn, :title, :author, :year, current_timestamp )"
            sqlparameters = { "isbn":isbn, "title":title, "author":author, "year":year }
            print(sqlInssert)
            print(sqlparameters)

            db.execute(sqlInssert, sqlparameters)
            db.commit()
            i=i+1
        else:
            i=i+1

    print(str(i-1) + " was instered!")


if __name__ == "__main__" :
    # with app.app_context():
        main()
