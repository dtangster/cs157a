

-- NOTE DONT COPY THEN JUST PASTE ALL FOR SOME REASON DOESNT WORK
-- COPY AND PASTE BY PARTS SO SAY ALL TABLES THEN COPY PASTE AND RUN TO POSTGRES
-- THEN COPY ALL VIEWS THEN PASTE AND RUN AGAIN...ETC 

--
-- TABLES
--

--POSTRGRES FREE "user" table already in used so renamed to user_inf
--use DOUBLE PRECISION INTSTEAD OF DOUBLE
DROP TABLE IF EXISTS user_inf cascade;
CREATE TABLE user_inf (
name VARCHAR(50),
email VARCHAR(50),
phone VARCHAR(12),
active_loan INT DEFAULT 0,
fee DOUBLE PRECISION DEFAULT 0.0,
password CHAR(128) NOT NULL,
salt CHAR(32) NOT NULL,
accesslevel INT DEFAULT 2,
last_login DATE,
PRIMARY KEY (email));

DROP TABLE IF EXISTS user_archive cascade;
CREATE TABLE user_archive (
name VARCHAR(50),
email VARCHAR(50),
phone VARCHAR(12),
active_loan INT DEFAULT 0,
fee DOUBLE PRECISION DEFAULT 0.0,
password CHAR(128) NOT NULL,
salt CHAR(32) NOT NULL,
accesslevel INT,
last_login DATE,
PRIMARY KEY (email));

DROP TABLE IF EXISTS book;
CREATE TABLE book (
bid INT,
title VARCHAR(50),
author VARCHAR(50),
pub_date DATE,
edition INT,
copies INT DEFAULT 0,
available INT DEFAULT 0,
PRIMARY KEY (bid));

DROP TABLE IF EXISTS loan cascade;
CREATE TABLE loan (
bid INT,
email VARCHAR(50),
overdue BOOLEAN,
loan_date DATE,
due_date DATE,
return_date DATE DEFAULT NULL,
PRIMARY KEY (loan_date, bid, email),
FOREIGN KEY (bid) REFERENCES book (bid),
FOREIGN KEY (email) REFERENCES user_inf (email));

DROP TABLE IF EXISTS review;
CREATE TABLE review (
bid INT REFERENCES book (bid),
email VARCHAR(50) REFERENCES user_inf (email),
rating_date DATE,
stars INT DEFAULT 0,
comment VARCHAR(512) DEFAULT 'No Comment');

-- Statuses: C (Cancelled), N (Nonavailability), P (Picked up), W (Waiting for pickup)
-- no Auto increment in postgres (use serial) and use ' ' (single) not  " " (double)
DROP TABLE IF EXISTS reservation cascade;
CREATE TABLE reservation (
reservation_id SERIAL NOT NULL ,
bid INT REFERENCES book (bid),
email VARCHAR(50) REFERENCES user_inf (email),
reserve_date DATE,
avail_date DATE,
status CHAR(1) DEFAULT 'N',
PRIMARY KEY (reservation_id, bid));




--
-- VIEWS
--

DROP VIEW IF EXISTS overdue_users;
CREATE VIEW overdue_users AS
SELECT name, email, bid, title, overdue, loan_date, due_date 
FROM user_inf NATURAL JOIN loan NATURAL JOIN book
WHERE overdue = TRUE
ORDER BY name, email, bid DESC;

DROP VIEW IF EXISTS debtors;
CREATE VIEW debtors AS
SELECT name, email, fee 
FROM user_inf WHERE fee > 0 
ORDER BY name, fee DESC;

DROP VIEW IF EXIST reservable_books;
CREATE VIEW reservable_books AS
SELECT * FROM book
WHERE available = 0;

DROP VIEW IF EXISTS reserved_books;
CREATE VIEW reserved_books AS
SELECT name, email, bid, title, author, edition, reserve_date
FROM reservation NATURAL JOIN user_inf NATURAL JOIN book
ORDER BY reservation_id;

DROP VIEW IF EXISTS available_books;
CREATE VIEW available_books AS
SELECT * FROM book where available > 0
ORDER BY title, author;

DROP VIEW IF EXISTS highest_rated_books;
CREATE VIEW highest_rated_books AS
SELECT bid, title, author, edition, email, stars, comment
FROM review NATURAL JOIN book
ORDER BY stars DESC, title, author, edition;

--
-- PROCEDURES MYSQL == FUNCTIONS 
--

-- Perform daily maintenance
drop function if exists perform_maintenance();
CREATE FUNCTION perform_maintenance() RETURNS void AS $$
BEGIN
    -- Archive users when they are inactive for 1 year
    INSERT INTO user_archive
        (SELECT * FROM user_inf
		WHERE  last_login < current_date - 365 
		 AND active_loan = 0);

    DELETE FROM user_inf WHERE email IN (SELECT email from user_archive);

    -- Cancel reservations not picked up after 5 days
    UPDATE reservation SET status = 'C' WHERE 
	 CURRENT_DATE >= (SELECT last_login from user_inf where last_login >= last_login + 5)  AND status = 'W';

    -- ONLY FOR SIMULATION
    -- Assume users picked up their reserved books
    UPDATE reservation SET status = 'P' WHERE status = 'W';
END; $$
LANGUAGE plpgsql;



-- Handle login and moving users out of archive
DROP FUNCTION IF EXISTS login(varchar, varchar);
CREATE FUNCTION login(IN email VARCHAR(50), IN password VARCHAR(128))
RETURNS void AS $$
BEGIN
    IF (email, password) IN (SELECT email, password FROM user_inf) THEN
        UPDATE user_inf SET last_login = CURRENT_DATE;
        SELECT email, accesslevel FROM user_inf WHERE user_inf.email = email;
    ELSEIF (email, password) IN (SELECT email, password FROM user_archive) THEN
        INSERT INTO user_inf (SELECT * FROM user_archive WHERE user_inf.email = email);
        DELETE FROM user_archive WHERE user_inf.email = email;
        UPDATE user_inf SET last_login = CURRENT_DATE;
        SELECT email, accesslevel FROM user_inf WHERE user_inf.email = email;
    END IF;
END; $$
LANGUAGE plpgsql;


-- Handle creating book reservations. Maximum of 3 reservations per user.

DROP FUNCTION IF EXISTS create_reservation(varchar, int);
CREATE FUNCTION create_reservation(IN email_ent VARCHAR(50), IN bid_ent INT)
RETURNS void AS $$
BEGIN
    IF (bid_ent) IN (SELECT bid FROM book WHERE available = 0) 
    THEN
        INSERT INTO reservation (bid, email, reserve_date) 
		VALUES (bid_ent, email_ent, CURRENT_DATE);
    END IF;
END; $$
LANGUAGE plpgsql;

--
-- TRIGGERS
--

-- Set last login date to current date when creating a user
-- IDK WHY THE HECK BEFORE INSERT TRIGGER DOESNT WORK T_T
-- BUT THIS WORKS THE SAME 

-- #1 sets current date to new inserted user 
drop function if exists init_login_date() cascade;
CREATE OR REPLACE FUNCTION init_login_date()
RETURNS TRIGGER AS $set_date$
    BEGIN    
            UPDATE user_inf 
            SET last_login = (select date from CURRENT_DATE)
            WHERE email = new.email;
    RETURN NEW;    
    END; 
$set_date$ LANGUAGE plpgsql;

drop trigger if exists init_login_date on user_inf cascade;
CREATE TRIGGER init_login_date
AFTER INSERT ON user_inf
FOR EACH ROW EXECUTE PROCEDURE init_login_date();

--   FOR DEBUGGIN
--   insert into user_inf values('hee', 'eea', '111-111-1111', 0, 0.0, 'abc', 'adfas', 2, '1111-11-02');  
--   delete from user_inf where email = 'eea';
--   select last_login from user_inf;




-- #2 When a book is checked out, update book count and due date
drop function if exists checkout() cascade;
CREATE OR REPLACE FUNCTION checkout()
RETURNS TRIGGER AS $checkout$
    BEGIN
        NEW.due_date = (select date from CURRENT_DATE);
	    UPDATE loan set due_date = NEW.due_date + 7 where email = new.email; 
	    UPDATE loan set loan_date = NEW.due_date where email = new.email;    
        UPDATE book SET available = available - 1 where bid = new.bid;
        UPDATE user_inf SET active_loan = active_loan + 1 where email = new.email;  
        RETURN NEW;         
    END;
$checkout$
LANGUAGE plpgsql;

drop trigger if exists checkout on loan;
CREATE TRIGGER checkout 
AFTER INSERT ON LOAN
FOR EACH ROW EXECUTE PROCEDURE checkout();


-- FOR DEBUGGIN 
-- insert into book values (100, 'title', 'u', '1111-11-11', 1, 3, 3);
-- insert into loan (bid, email, overdue, loan_date, due_date) values (100, 'eea', false, '2222-12-22', '2222-12-13' );
-- insert into user_inf values('hee', 'eea', '111-111-1111', 0, 0.0, 'abc', 'adfas', 2, '1111-11-02');  
-- delete from user_inf where email = 'eea';
-- delete from loan where email = 'eea';
-- select name, email, active_loan from user_inf;
-- insert into reservation(bid, email, reserve_date, avail_date, status) values (100, 'eea', '2222-12-22', '2222-12-22', 'N');


-- 3) When a return date is set, update book count and reservation

drop function if exists return_book() cascade;
CREATE OR REPLACE FUNCTION return_book()
RETURNS TRIGGER AS $return_book$
BEGIN
    IF  OLD.return_date is NULL AND NEW.return_date is NOT NULL 
	      AND old.bid  in (select b.bid from reservation b where b.bid = old.bid)
    THEN 
        --UPDATE book SET available = available + 1 WHERE bid = new.bid;
        UPDATE user_inf SET active_loan = active_loan - 1 WHERE email = NEW.email;
			UPDATE reservation SET status = 'W', avail_date = (select date from CURRENT_DATE)
				   WHERE bid = NEW.bid AND status = 'N' and 	reservation_id = (SELECT 
					min(r.reservation_id) from reservation r where new.bid = r.bid 
				   );
    ELSEIF OLD.return_date is NULL AND NEW.return_date is NOT NULL 
    THEN
        UPDATE book SET available = available + 1 WHERE bid = new.bid;
        UPDATE user_inf SET active_loan = active_loan - 1 WHERE email = NEW.email;
    END IF;
    
    RETURN NEW;
END;
$return_book$
LANGUAGE plpgsql;


drop trigger if exists return_book on loan;
CREATE TRIGGER return_book 
AFTER UPDATE ON LOAN
FOR EACH ROW EXECUTE PROCEDURE return_book();



-- 4# Do checks when a reservation is made
drop function if exists reserve_book() cascade;
CREATE OR REPLACE FUNCTION reserve_book()
RETURNS TRIGGER AS $reserve_book$
BEGIN
     UPDATE reservation SET reserve_date = (select date from CURRENT_DATE);
     IF new.bid IN (SELECT bid from book WHERE available = 0) AND
          new.bid NOT IN (SELECT bid from reservation)	 
        THEN
           UPDATE reservation SET avail_date =  (select date from CURRENT_DATE);
           UPDATE reservation SET status = 'W';
           UPDATE book SET available = available - 1 WHERE bid = new.bid;
     ELSE
        UPDATE reservation SET status = 'N' WHERE new.bid = bid;
     END IF;
     RETURN NEW;
END; 
$reserve_book$
LANGUAGE plpgsql;

drop trigger if exists reserve_book on reservation;
CREATE TRIGGER reserve_book
AFTER INSERT ON reservation
FOR EACH ROW EXECUTE PROCEDURE reserve_book();


-- 5# Do checks when a book becomes available
drop function if exists update_reservation() cascade;
CREATE OR REPLACE FUNCTION update_reservation()
RETURNS TRIGGER AS $update_reservation$
BEGIN
    IF old.status = 'N' AND new.status = 'W' THEN
        UPDATE reservation SET avail_date =  (select date from CURRENT_DATE);
        --UPDATE book SET available = available - 1 WHERE bid = new.bid;
    ELSEIF old.status = 'W' AND new.status = 'C' THEN
        UPDATE book SET available = available + 1 WHERE bid = new.bid;		
    ELSEIF old.status != 'P' AND new.status = 'P' THEN
        UPDATE user_inf SET active_loan = active_loan + 1 WHERE email = new.email;
    END IF;
    RETURN NEW;
END;
$update_reservation$
LANGUAGE plpgsql;

drop trigger if exists update_reservation on reservation;
CREATE TRIGGER update_reservation
AFTER UPDATE ON reservation
FOR EACH ROW EXECUTE PROCEDURE update_reservation();

