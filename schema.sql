USE test;

CREATE TABLE traces (

	id INT AUTO_INCREMENT,
	day DATE NOT NULL,
	hour TIME NOT NULL,
	x REAL NOT NULL,
	y REAL NOT NULL,
	z REAL NOT NULL,
	freq REAL NOT NULL,
	map VARCHAR(255) NOT NULL DEFAULT 'skinmask',
	bumpmap VARCHAR(255) NOT NULL DEFAULT 'blurotsu100trans',
	sound VARCHAR(255) NOT NULL UNIQUE,

	PRIMARY KEY(id)
);

