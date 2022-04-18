CREATE TABLE feedback (author varchar(128), text varchar(512));
CREATE TABLE users (login varchar(128), password varchar(128), is_admin integer, auth_cookie varchar(64));
INSERT INTO users VALUES ("admin", "123", 1, "76846583");
INSERT INTO users VALUES ("non_admin", "123", 0, "34364");