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

CREATE  TABLE user (
  uid  int NOT NULL,
  default_wid int NOT NULL,
  fullname varchar(255) NOT NULL,
  PRIMARY KEY (uid),
  FOREIGN KEY  (default_wid) REFERENCES workspace(wid)
);

CREATE TABLE time_entry (
  teid int NOT NULL,
  pid int NOT NULL,
  uid int NOT NULL,
  description LONGTEXT,
  start_date  DATETIME NOT NULL,
  stop_date DATETIME NOT NULL,
  duration DOUBLE NOT NULL 
  updated DATETIME NOT NULL,



)
