create table main.comments
(
    id           integer
        constraint comments_pk
            primary key autoincrement,
    content      TEXT    default '',
    author       TEXT              not null,
    root_comment integer default -1,
    date_posted  integer           not null,
    comment_type integer default 0 not null,
    comment_page integer           not null,
    replies      TEXT    default '[]'
);

create table main.images
(
    id            integer         not null
        constraint images_pk
            primary key,
    title         TEXT default '',
    caption       TEXT default '',
    author        TEXT default '' not null,
    date_uploaded integer,
    image         BLOB            not null
);

create table main.posts
(
    id          integer not null
        constraint posts_pk
            primary key autoincrement,
    title       TEXT    default 'Untitled',
    content     TEXT,
    author      TEXT    not null,
    date_posted integer,
    likes       integer default 0,
    comments    TEXT    default '[]'
);

create table main.sqlite_master
(
    type     TEXT,
    name     TEXT,
    tbl_name TEXT,
    rootpage INT,
    sql      TEXT
);

create table main.sqlite_sequence
(
    name,
    seq
);

create table main.tokens
(
    id          TEXT    not null
        constraint tokens_pk
            unique,
    username    TEXT    not null,
    valid_until integer not null
);

create table main.users
(
    username     TEXT not null
        constraint users_pk
            primary key,
    date_created integer,
    password     TEXT not null,
    followers    TEXT default '[]',
    posts        TEXT default '[]',
    following    TEXT default '[]',
    liked_posts  TEXT default '[]',
    bio          TEXT default ''
);

