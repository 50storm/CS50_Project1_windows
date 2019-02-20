echo setting flask
SET FLASK_APP=application.py
SET FLASK_DEBUG=1
#SET FLASK_DEBUG=0
SET DATABASE_URL=postgres://hiroshi:Tera54hiro@localhost/bookreview
echo flask run
flask run
