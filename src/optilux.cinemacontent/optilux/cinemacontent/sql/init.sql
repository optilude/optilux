/* This file contains table definitions for the optilux
  cinemas example.
 */

create database if not exists optilux;
use optilux;

-- Screenings
create table if not exists screening (
    screeningId integer unsigned not null auto_increment primary key,
    cinemaCode char(4) not null,
    filmCode char(4) not null,
    showTime datetime not null,
    remainingTickets integer unsigned not null,
    index showing_cinemaCode(cinemaCode),
    index showing_filmCode(filmCode),
    index showing_showTime(showTime),
    index showing_remainingTickets(remainingTickets)
) engine=InnoDB;

-- Reservations
create table if not exists reservation (
    reservationId integer unsigned not null auto_increment primary key,
    screeningId integer unsigned not null,
    numTickets tinyint unsigned not null,
    customerName varchar(64) not null,
    index reservation_numTickets(numTickets),
    foreign key(screeningId)
        references screening(screeningId)
            on update restrict
            on delete restrict
) engine=InnoDB;
