create table posts
(
    id          integer not null
        constraint posts_pk
            primary key autoincrement,
    title       TEXT    default 'Untitled',
    content     TEXT,
    author      TEXT    not null,
    date_posted integer,
    likes       integer default 0
);

create table tokens
(
    id          TEXT    not null
        constraint tokens_pk
            unique,
    username    TEXT    not null,
    valid_until integer not null
);

create table users
(
    username     TEXT not null
        constraint users_pk
            primary key,
    date_created integer,
    password     TEXT not null,
    followers    TEXT default '[]',
    posts        TEXT default '[]',
    following    TEXT default '[]',
    liked_posts  TEXT default '[]'
);