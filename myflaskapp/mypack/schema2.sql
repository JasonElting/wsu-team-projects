drop table if exists entries;
create table entries(
	id integer autoincrement,
	title text not null,
	tag text not null primary key,
	location text not null
);
