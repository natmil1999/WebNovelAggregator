create table fictions
(
    fiction_id INTEGER
        primary key,
    name       TEXT                  not null,
    url        TEXT                  not null
        unique,
    Patreon_RR int  default 1        not null,
    Author     TEXT default 'Filler' not null
);

create table chapters
(
    id         INTEGER
        primary key,
    fiction_id INTEGER
        references fictions
            on delete cascade,
    url        TEXT not null
        unique,
    read       INTEGER default 0,
    title      TEXT not null
);

