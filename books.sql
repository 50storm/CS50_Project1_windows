DROP TABLE books;

CREATE TABLE books (
    isbn character varying(10) NOT NULL,
    title character varying(255) NOT  NULL,
    author character varying(255) NOT NULL,
    year  smallint  NOT NULL,
    created_at timestamp without time zone
);



INSERT INTO books ( isbn, title, author, year, created_at )
VALUES            ( '9999999', 'book title','author',2010,current_timestamp);
