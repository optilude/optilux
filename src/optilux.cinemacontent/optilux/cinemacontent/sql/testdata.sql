-- Create some test data in the optilux database
-- Note that since the UI logic only shows things in the near future,
-- you may need to run this every few days :)

use optilux;

-- Assume there are cinema codes C1, C2, C3 and film codes F1, F2 and F3
-- You will need to populate these in Plone as well

insert into screening (cinemaCode, filmCode, showTime, remainingTickets) 
values 
       -- Cinema 1
       ('C1', 'F1', date_add(now(), interval 24 hour), 100),
       ('C1', 'F1', date_add(now(), interval 36 hour), 100),
       ('C1', 'F1', date_add(now(), interval 36 hour),  50),
       
       ('C1', 'F2', date_add(now(), interval 18 hour), 100),
       ('C1', 'F2', date_add(now(), interval 72 hour), 100),

       ('C1', 'F3', date_add(now(), interval 33 hour), 100),
       ('C1', 'F3', date_add(now(), interval 36 hour), 100),
       ('C1', 'F3', date_add(now(), interval 39 hour),  50),

       -- Cinema 2
       ('C2', 'F1', date_add(now(), interval 12 hour),  30),
       ('C2', 'F1', date_add(now(), interval 36 hour),  40),
       ('C2', 'F1', date_add(now(), interval 72 hour),  50),

       ('C2', 'F2', date_add(now(), interval 40 hour), 100),
       ('C2', 'F2', date_add(now(), interval 40 hour),  20),
       ('C2', 'F2', date_add(now(), interval 80 hour), 100),

       ('C2', 'F3', date_add(now(), interval 72 hour), 100),
       ('C2', 'F3', date_add(now(), interval 80 hour), 100),
       ('C2', 'F3', date_add(now(), interval 90 hour),  50),
       
       -- Cinema 3
       ('C3', 'F1', date_add(now(), interval  4 hour), 300),
       ('C3', 'F1', date_add(now(), interval 12 hour), 200),
       ('C3', 'F1', date_add(now(), interval 18 hour), 100),

       ('C3', 'F2', date_add(now(), interval  4 hour), 300),
       ('C3', 'F2', date_add(now(), interval 12 hour), 350),

       ('C3', 'F3', date_add(now(), interval 25 hour), 250),
       ('C3', 'F3', date_add(now(), interval 39 hour),  90),
       ('C3', 'F3', date_add(now(), interval 47 hour),  90);
