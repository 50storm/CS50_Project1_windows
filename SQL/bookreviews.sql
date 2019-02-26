DROP TABLE bookreviews;

CREATE TABLE bookreviews (
    isbn  character varying(10) NOT NULL,
    user_id integer NOT  NULL,
    rate    integer NOT  NULL,
    comment text NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
	PRIMARY KEY (isbn, user_id)
);


INSERT INTO bookreviews  ( isbn,  user_id, rate,    comment, created_at )
VALUES                   ( '0380795272', 1,    4,   'Great!', current_timestamp);


