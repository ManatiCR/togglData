CREATE TABLE workspace (
wid int NOT NULL,
name varchar(120) NOT NULL,
PRIMARY KEY (wid));

CREATE TABLE client (
cid int NOT NULL,
wid int NOT NULL,
name varchar(120) NOT NULL,
PRIMARY KEY (cid),
FOREIGN KEY (wid) REFERENCES workspace(wid)
);

CREATE TABLE project (
pid int NOT NULL,
wid int NOT NULL,
cid int NOT NULL,
name varchar(120) NOT NULL,
PRIMARY KEY (pid),
FOREIGN KEY (wid) REFERENCES workspace(wid),
FOREIGN KEY (cid) REFERENCES client(cid)
);
