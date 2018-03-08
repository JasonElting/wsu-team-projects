drop table if exists entries;
create table entries (
	id integer primary key autoincrement,
	title text not null,
	tag text not null unique,
	location text not null
);
