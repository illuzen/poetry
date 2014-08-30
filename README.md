Poetry

To run:

cd ./src/python
python poetry.py

This will run the program on all the documents in ./doc/texts

The program calculates same-sentence frequency for all pairs of words in the document and plots the variances of that frequency with matplotlib and prints those variances to ./src/var_file  

It also stores the relationships between the words in a neo4j graph database

For development, use ./doc/test_texts instead of ./doc/texts to reduce computation time.

./miscellania has various tangentially related scripts, including 

-database_init.sql: an sql script to create a mysql database for this same idea
-keledones.py: a python script containing classes that could be used to organize documents
-luau.py: a part of speech hidden-markov-model
-nltk_example.py: an example of how to use nltk
-py2neo_example.py: an example of how to connect python to neo4j

