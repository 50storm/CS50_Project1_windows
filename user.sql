DROP TABLE users;

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY ,
    username character varying(255) NOT NULL,
    firstname character varying(255)  NULL,
    lastname character varying(255) NULL,
    password character varying(255) NOT NULL,
    created_at timestamp without time zone
);



INSERT INTO users (username, firstname, lastname, password, created_at )
VALUES            ('Hakata',  'Hiroshi' , 'Igarashi','hiro1128' , current_timestamp);
