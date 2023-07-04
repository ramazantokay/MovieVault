create table if not exists actors (
	actorId text,
	primaryName text,
	birthYear int,
	deathYear int,
	gender text,
	primary key (actorId)
);
create table if not exists directors (
	directorId text,
	primaryName text,
	primary key (directorId)
);
create table if not exists movies (
	movieId text,
	originalTitle text,
	startYear int,
	averageRating decimal,
	numVotes int,
	primary key (movieId)
);
create table if not exists directed (
	movieId text,
	directorId text,
	primary key (movieId, directorId),
	foreign key (movieId) references movies(movieId) on delete cascade,
	foreign key (directorId) references directors(directorId) on delete cascade
);
create table if not exists genres (
	movieId text,
	genre text,
	primary key (movieId, genre),
	foreign key (movieId) references movies(movieId) on delete cascade
);
create table if not exists casts (
	movieId text,
	actorId text,
	characters text,
	primary key (movieId, actorId),
	foreign key (movieId) references movies(movieId) on delete cascade,
	foreign key (actorId) references actors(actorId) on delete cascade
);
create table if not exists plans (
	planId serial,
	planName text,
	resolution text,
	maxParallelSessions int,
	monthlyFee int,
	primary key (planId)
);
create table if not exists customers (
	customerId serial,
	email text,
	password text,
	firstName text,
	lastName text,
	sessionCount int,
	planId int,
	primary key (customerId),
	foreign key (planId) references plans(planId) on delete cascade,
	unique (email)
);
create table if not exists watched (
	customerId serial,
	movieId text,
	primary key (customerId, movieId),
	foreign key (customerId) references customers(customerId) on delete cascade,
	foreign key (movieId) references movies(movieId) on delete cascade
);

/* these inserted values are for testing purposes, you can play with the database as much as you want. */ 
insert into plans(planName, resolution, maxParallelSessions, monthlyFee) 
values 
	('Basic', '720P', 2, 30),
	('Advanced', '1080P', 4, 50),
	('Premium', '4K', 10, 90);
	

insert into customers(email, password, firstName, lastName, sessionCount, planId) 
values 
	('cj@mp2.com','pass123','Carl','Johnson', 0, 1),
	('ryder@mp2.com','pass123','Lance','Wilson', 0, 2),
	('bigsmoke@mp2.com','pass123','Melvin','Harris', 0, 3);
