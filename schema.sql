drop table if exists auth;
create table auth (
    id integer primary key autoincrement,
    password text not null,
    key char(16)
);

drop table if exists album;
create table album (
    id integer primary key autoincrement,
    title text not null,
    artist text not null
);

drop table if exists file;
create table file (
    id integer primary key autoincrement,
    album integer not null,
    path text not null
);
