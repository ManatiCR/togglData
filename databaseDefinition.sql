CREATE TABLE workspace (
wid int unsigned NOT NULL,
name varchar(120) NOT NULL,
PRIMARY KEY (wid));

CREATE TABLE client (
cid int unsigned NOT NULL,
wid int unsigned NOT NULL,
name varchar(120) NOT NULL,
PRIMARY KEY (cid),
FOREIGN KEY (wid) REFERENCES workspace(wid)
);

CREATE TABLE project (
pid int unsigned NOT NULL,
wid int unsigned NOT NULL,
cid int unsigned NOT NULL,
name varchar(120) NOT NULL,
PRIMARY KEY (pid),
FOREIGN KEY (wid) REFERENCES workspace(wid),
FOREIGN KEY (cid) REFERENCES client(cid)
);

CREATE  TABLE user (
  uid int unsigned NOT NULL,
  default_wid int unsigned NOT NULL,
  fullname varchar(255) NOT NULL,
  PRIMARY KEY (uid),
  FOREIGN KEY  (default_wid) REFERENCES workspace(wid)
);

CREATE TABLE time_entry (
  teid int unsigned NOT NULL,
  pid int unsigned ,
  uid int unsigned NOT NULL,
  description LONGTEXT,
  start_date DATETIME NOT NULL,
  stop_date DATETIME NOT NULL,
  duration DOUBLE NOT NULL,
  updated DATETIME NOT NULL,
  PRIMARY KEY (teid),
  FOREIGN KEY (uid) REFERENCES user(uid),
  FOREIGN KEY (pid) REFERENCES project(pid)
);

CREATE TABLE tag (
  tid int unsigned NOT NULL AUTO_INCREMENT,
  name varchar(255) NOT NULL,
  PRIMARY KEY (tid)
);

CREATE TABLE time_entry_tag (
  id int unsigned NOT NULL AUTO_INCREMENT,
  teid int unsigned NOT NULL,
  tid int unsigned NOT NULL,
  PRIMARY KEY (id),
  FOREIGN KEY (teid) REFERENCES time_entry(teid),
  FOREIGN KEY (tid) REFERENCES tag(tid)
);
