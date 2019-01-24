CREATE TABLE bookreviews (
    isbn  character varying(255) NOT NULL,
    user_id integer NOT  NULL,
    comment character varying(255) NOT NULL,
    created_at timestamp without time zone,
	PRIMARY KEY (isbn, user_id)
);


INSERT INTO bookreviews ( isbn, user_id, comment, created_at )
VALUES            ( '0380795272', 2,'Great!', current_timestamp);


username = request.form.get("isbn").strip()
user_id= request.form.get("user_id").strip()
comment   = request.form.get("comment").strip()
insertSQL ="INSERT INTO bookreviews (isbn, user_id, comment)VALUES (:isbn, :user_id, :comment)"

users = db.execute(

            {"username":username, "user_id":user_id, "comment":comment}
 )