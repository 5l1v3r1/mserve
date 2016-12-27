drop table if exists auth;
create table auth (
    id integer primary key autoincrement,
    password text not null,
    key char(16)
);

drop table if exists artist;
create table artist (
    id integer primary key autoincrement,
    name text not null
);

drop table if exists album;
create table album (
    id integer primary key autoincrement,
    artist integer not null,
    title text not null
);

drop table if exists file;
create table file (
    id integer primary key autoincrement,
    album integer not null,
    path text not null
);
