Poetry


Scripts:
================================================================
+ Same-sentence frequency variance calculator: poetry.py
================================================================
To run:

cd ./src/python
python poetry.py

This will run the program on all the documents in ./doc/texts

The program calculates same-sentence frequency for all pairs of words in the document and plots the variances of that frequency with matplotlib and prints those variances to ./src/var_file  

It also stores the relationships between the words in a neo4j graph database

For development, use ./doc/test_texts instead of ./doc/texts to reduce computation time.

================================================================
+ Simple wikipedia scraper: scraper.py
================================================================

================================================================
+ Hierarchical clustering class: clustering_demo.py
================================================================

================================================================
+ Automatic summarizer: summarizer.py
================================================================

================================================================
+ Flask server: server.py
================================================================

To add a url route, add the following to server.py:

@app.route('/my_url')
def my_function():
	# do python stuff

if you want to serve an html file, use 
app.send_static_file('my_html.html')

For more info, see the examples in server.py or look thru
http://flask.pocoo.org/docs/0.10/quickstart/#quickstart

Our server's IP is http://130.211.246.132:5000/

================================================================
+ Miscellania: ./miscellania/
================================================================
./miscellania has various tangentially related scripts, including 

-database_init.sql: an sql script to create a mysql database for this same idea
-keledones.py: a python script containing classes that could be used to organize documents
-luau.py: a part of speech hidden-markov-model
-nltk_example.py: an example of how to use nltk
-py2neo_example.py: an example of how to connect python to neo4j

