drop table if exists auth;
create table auth (
    id integer primary key autoincrement,
    password text not null,
    key char(16)
);

drop table if exists files;
create table files (
    id integer primary key autoincrement,
    track blob(16) not null,
    release blob(16) not null,
    path varchar not null
);

drop table if exists genres;
create table genres (
    release blob(16) not null,
    genre varchar not null
);

drop table if exists releases;
create table releases (
    id blob(16) primary key,
    title varchar,
    year integer
);

drop table if exists credits;
create table credits (
    release blob(16) not null,
    artist varchar not null
);
