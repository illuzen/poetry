from py2neo import neo4j, rel, node


def persist_graph(frequency_matrix):
	session = cypher.Session("http://localhost:7474")

	tx = session.create_transaction()
	for word1 in frequency_matrix.keys():
		for word2 in frequency_matrix[word1].keys():
			if (word1 != word2):
				tx.append("MERGE (word1:THING { meme: '" + word1 + "'})"
							 "MERGE (word2:THING { meme: '" + word2 + "'})"
							 "CREATE (word1)-[:SAME_SENTENCE { cond_prob: " + str(frequency_matrix[word1][word2]) + "}]->(word2)")
	tx.execute()
	print 'executed'
	tx.commit()
	
def persist_graph( frequency_matrix):
    nodes = []
    for word1 in frequency_matrix.keys():
        if word1 not in nodes:
            nodes.append(word1)
        for word2 in frequency_matrix[word1].keys():
            if word2 not in nodes:
                nodes.append(word2)


def graph_push( d ):
    """
    Temporary way of pushing a dict of dicts to a neo4j database. Will be added
    to neo4j later.
    """
    neo4j._add_header('X-Stream', 'true;format=pretty')
    word_set = set( d.keys() )
    for words in d.values():
        word_set = word_set.union( set( words.keys() ) ) 

    idx = { word : i for i, word in enumerate( word_set ) }
    nodes = [ {'word':word} for word in word_set ]
    relations = []

    for from_word, edges in d.items():
        for to_word, p in edges.items():
            relations.append( ( idx[from_word], "SAME_SENTENCE", idx[to_word], {"Conditional Probability": p} ) )

    arguments = nodes + relations

    g = neo4j.GraphDatabaseService()
    g.clear()
    g.create( *arguments )

def graph_pull():
    """
    Temporary way to pull the data from the graph into a dictionary of
    dictionaries.
    """

    d = {}
    g = neo4j.GraphDatabaseService()
    rels = [ rel for rel in g.match() ]

    for rel in rels:
        start = rel.start_node.get_properties()['word']
        end = rel.end_node.get_properties()['word']
        p = rel._properties['Conditional Probability']

        if start in d.keys():
            d[ start ][ end ] = p
        else:
            d[ start ] = { end: p }

    return d