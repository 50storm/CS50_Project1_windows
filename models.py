from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
class Flight(db.Model):
    __tablename__="flights"
    id = db.Column(db.Integer, primary_key=True)
    origin=db.Column(db.String, nullable=False)
    destination=db.Column(db.String, nullable=False)
    duration=db.Column(db.Integer, nullable=False)

    def add_passenger(self, name):
        p = Passenger(name=name, flight_id=self.id)
        db.session.add(p)
        db.session.commit()

class Passenger(db.Model):
     __tablename__="passengers"
     id = db.Column(db.Integer, primary_key=True)
     name=db.Column(db.String, nullable=False)
     flight_id=db.Column(db.Integer, db.ForeignKey("flights.id"),nullable=False)


# class User(db.Model):
#     __tablename__="users"
#     id = db.Column(db.Integer, primary_key=True)
#     first_name=db.Column(db.String, nullable=False)
#     last_name=db.Column(db.String, nullable=False)
#     password=db.Column(db.String, nullable=False)
#





#   CREATE TABLE flights (
#       id SERIAL PRIMARY KEY,
#       origin VARCHAR NOT NULL,
#       destination VARCHAR NOT NULL,
#       duration INTEGER NOT NULL
#   );

# INSERT INTO flights (origin,destination,duration) VALUES ('New York','Paris',300);

# CREATE TABLE users (
    # id SERIAL PRIMARY KEY,
    # first_name character varying(255) NOT NULL,
    # last_name character varying(255) NOT NULL,
    # password character varying(255) NOT NULL,
    # created_at timestamp without time zone
# );
