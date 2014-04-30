Poetry

A project to inspire creativity through poetry suggestion.


-------------
Database Info
-------------

Initializing:
	>$ mysql -u USERNAME -p < database_init.sql

Organization:
	Database name; poetry

Tables
+------------------+
| Tables_in_poetry |
+------------------+
| authors          |
| edges            |
| memes            |
| metrics          |
| source_types     |
| sources          |
+------------------+
	
Sources - texts that were analyzed.
+--------------+--------------+------+-----+---------+----------------+
| Field        | Type         | Null | Key | Default | Extra          |
+--------------+--------------+------+-----+---------+----------------+
| id           | int(11)      | NO   | PRI | NULL    | auto_increment |
| title        | varchar(256) | NO   |     | NULL    |                |
| length_words | int(11)      | YES  |     | NULL    |                |
| num_unique   | int(11)      | YES  |     | NULL    |                |
| date         | date         | YES  |     | NULL    |                |
| source_type  | int(11)      | YES  |     | NULL    |                |
| author       | int(11)      | YES  |     | NULL    |                |
+--------------+--------------+------+-----+---------+----------------+

Edges - two memes that share some sort of relationship defined by metric type.
+---------------------+--------------+------+-----+---------+----------------+
| Field               | Type         | Null | Key | Default | Extra          |
+---------------------+--------------+------+-----+---------+----------------+
| id                  | int(11)      | NO   | PRI | NULL    | auto_increment |
| normalized_relation | decimal(6,6) | YES  |     | NULL    |                |
| relation            | decimal(6,6) | YES  |     | NULL    |                |
| meme1               | int(11)      | YES  |     | NULL    |                |
| meme2               | int(11)      | YES  |     | NULL    |                |
| metric_type         | int(11)      | YES  |     | NULL    |                |
+---------------------+--------------+------+-----+---------+----------------+

authors - author's of the sources
metrics - metric name that describes an edge
memes - meaningful set of knowledge, aka words
source_type - type of source the information came from (digital or otherwise)
