# database.py
# Contact: Jacob Schreiber
#          jmschreiber91@gmail.com

'''
This is a connector between python and a SQL database. Allows for an OO way of
issuing SQL commands.

There are two objects here, a Database and a Table. A Database is a connection
to the Database of choice, allowing you to issue arbitrary SQL commands, and
also to get Table objects. 

>>> db = SQLDatabase( db="cheeses", user="jim", password="1hGaj29Kajh", 
        host="127.0.0.1")
>>> db.execute( "SELECT * FROM cheese_list" )
(( 'cheddar', 'CHE' ), ( 'american', 'AME', ), ( 'gruye', 'GRU' ))
>>> db.execute( "INSERT INTO cheese_list VALUES ('mozarella', 'MOZ')" )
>>> db.execute( "SELECT * FROM cheese_list" )
(( 'cheddar', 'CHE' ), ( 'american', 'AME', ), ( 'gruye', 'GRU' ),
    ('mozarella', 'MOZ'))
>>> db.execute( "DELETE FROM cheese_list WHERE name LIKE '%%'" )
>>> db.execute( "SELECT * FROM cheese_list" )
()

You can also get tables, which allow you to have an OO interface to that specific
table. Assuming that the previous commands did not occur, you can do the following:

>>> table = db.get_table( "cheese_list" )
>>> table.column_names
[ 'name', 'tag' ]
>>> table.column_types
[ 'varchar', 'varchar' ]
>>> table.read()
(( 'cheddar', 'CHE' ), ( 'american', 'AME', ), ( 'gruye', 'GRU' ))
>>> table.read( columns=["name"])
(( 'cheddar' ), ( 'american' ), ( 'gruye' ))
>>> table.read( columns=["name"], values=["am%"])
(( 'american' ))
>>> table.insert( values=('mozarella', 'MOZ') )
>>> table.read()
(( 'cheddar', 'CHE' ), ( 'american', 'AME', ), ( 'gruye', 'GRU' ),
    ('mozarella', 'MOZ'))
>>> table.delete( columns=["name"], values=["mozarella"] )
>>> table.read()
(( 'cheddar', 'CHE' ), ( 'american', 'AME', ), ( 'gruye', 'GRU' ))
>>> table.insert( values=('MOZ', 'mozarella'))
>>> table.read()
(( 'cheddar', 'CHE' ), ( 'american', 'AME', ), ( 'gruye', 'GRU' ),
    ('MOZ', 'mozarella'))
>>> table.delete( columns=["name"], values=["mozarella"] )
>>> table.read()
(( 'cheddar', 'CHE' ), ( 'american', 'AME', ), ( 'gruye', 'GRU' ),
    ('MOZ', 'mozarella'))
>>> table.delete( columns=["name"], values=["MOZ"] )
>>> table.read()
(( 'cheddar', 'CHE' ), ( 'american', 'AME', ), ( 'gruye', 'GRU' ))
>>> table.insert( columns=["tag", "name"], values=["MOZ", "mozarella"])
>>> table.read()
(( 'cheddar', 'CHE' ), ( 'american', 'AME', ), ( 'gruye', 'GRU' ),
    ('mozarella', 'MOZ'))
'''

try:
    import MySQLdb
    mySQL = True
except:
    mySQL = False

try:
    from py2neo import neo4j, rel, node
    neo = True
except:
    neo = False

import itertools as it

join = lambda d, values: '{}'.format( d ).join( "'{}'".format( v ) for v in map( str, values ) )

class SQLDatabase( object ):
    '''
    Represents a SQL database. 
    '''

    def __init__( self, db, user, password, host ):
        '''
        Take in the credentials for the server and connect to it, connecting
        to a specific database on the server.
        '''
        if not mySQL:
            raise ImportError( "Must install mySQLdb before using." )

        self.db = MySQLdb.connect( host, user, password, db )
        self.cursor = self.db.cursor()

    def execute( self, statement ):
        '''
        Allows the user to execute a specific SQL command. If an error is
        raised, raise an error.
        '''

        self.cursor.execute( statement )
        self.db.commit()
        return self.cursor.fetchall()

    def get_table( self, table ):
        '''
        Make a table object for a certain table.
        '''

        return Table( self, table )


    def read_table( self, table, columns=None, values=None ):
        '''
        A wrapper allowing you to read a table.
        '''

        table = self.get_table( table )
        return table.read( columns=columns, values=values ) 

class Table( object ):
    '''
    Represents a table in the database. Allows you to query that table directly
    instead of looking at the database level.
    '''

    def __init__( self, db, name ):
        '''
        Store the name. We can't actually 'login' to a table, to we'll just
        only call from that table in the future.
        '''
        self.db = db
        self.name = name

    @property
    def columns( self ):
        return self.db.execute( "SHOW COLUMNS FROM {}".format( self.name ) )

    @property
    def column_type_dict( self ):
        return { key: value for key, value, _, _, _, _ in self.columns }

    @property
    def column_names( self ):
        return map( lambda x: x[0], self.columns )

    @property
    def column_types( self ):
        return map( lambda x: x[1], self.columns )

    def read( self, columns=None, values=None ):
        '''
        Read certain columns from the table, or all by default.
        '''

        query = "SELECT {} FROM {}".format( 
            ','.join( columns ) if columns else '*', self.name )
        if values:
            query += " WHERE {}".format( self._build_clauses( values, columns ) )

        return self.db.execute( query )

    def insert( self, values, columns=None ):
        '''
        Allows you to insert one row into the database. Assume the ordering
        is as specified in the database unless columns are specified, then
        use that ordering.
        '''

        self.db.execute( "INSERT INTO {} {} VALUES ({})".format(
            self.name, "({})".format( ','.join( columns ) ) if columns else "",
            ",".join( "'{}'".format( str(v) ) for v in values  ) )  )

    def delete( self, entry, columns=None ):
        '''
        Allows you to delete anything matching this entry.
        '''

        self.db.execute( "DELETE FROM {} WHERE {}".format(
            self.name, self._build_clauses( entry, columns ) ) )

    def _build_clauses( self, values, columns=None ):
        '''
        A private function which will take a tuple of values, ordered according
        to the column order in the database, and build an appropriate set of
        clauses including "IS NULL", "=", "LIKE", and quotations as appropriate.
        '''

        # If columns are provided, they may be looking fur a custom ordering
        # of values, so use that. Else, use the natural ordering
        columns = columns or self.column_names
        column_type_dict = self.column_type_dict

        # Store the clauses for later use.
        clauses = []

        # Iterate through the column-value pairs, assuming that if they gave
        # a column and not a value that they don't care what that value is.
        for column, value in it.izip_longest( columns, values ):
            column_type = self.column_type_dict[ column ]

            # If the entry is None, they don't care what it is and
            # thus use a wildcard
            if value is None:
                value = '*'

            # Remove any extra white space that may be there
            value = value.strip()

            # SQL NULL is the same as the string None, not the datatype None
            if value == "None": 
                clauses.append( "{} IS NULL".format( column ) )

            # If the cell type is a varchar..
            elif 'varchar' in column_type:
                if value[-1] != '*':  
                    # If they are not looking for a wild card, look for exact match  
                    clauses.append( "{} = '{}'".format( column, value ) )
                else:
                    # Otherwise, allow for wild card
                    clauses.append( "{} LIKE '%{}%'".format(column, value[:-1]))
            elif 'float' in column_type or 'int' in column_type:
                clauses.append( "{} = {}".format( column, value ) )

        return ' AND '.join( clauses ) or None

class Neo4jDatabase( object ):
    """
    A wrapper for a Neo4j database. INCOMPLETE.
    """

    def __init__( self, host="http://localhost:7474/db/data" ):
        if not neo:
            raise ImportError( "Must install py2neo before using." )

        self.db = neo4j.GraphDatabaseService( host )
        self.nodes = {}

    def add_node( self, dictionary ):
        """
        Add a node to the graph. Pass in a dictionary of data for that node to
        store.
        """

        self.db.create( node( dictionary ) )

    def add_nodes( self, dictionaries ):
        """
        Batch add multiple nodes to the graph. Pass in a list of dictionaries 
        of data for that node to store. 
        """

        self.db.create( *[ node( d ) for d in dictionaries ] )


    def add_edge( self, tup ):
        """
        Add a single edge to the graph. Pass in a tuple consisting of
        ( from, label, to ). Example:

        ( 0, "KILLED", 5 )
        """

        self.db.create( rel( tup[0], tup[1], tup[2] ) )

    def add_edges( self, tups ):
        """
        Batch add multiple edges to the graph. Pass in a tuple consisting of
        ( from, label, to ). Example:

        [(0, "LOVES", 1 )
        (2, "LOVES", 1 )
        (3, "HATES", 2 )]
        """

        self.db.create( *[ rel( tup[0], tup[1], tup[2] ) for tup in tups ] )

def graph_push( d ):
    """
    Temporary way of pushing a dict of dicts to a neo4j database. Will be added
    to neo4j later.
    """

    word_set = set( d.keys() )
    for words in d.values():
        word_set = word_set.union( set( words.keys() ) ) 

    idx = { word : i for i, word in enumerate( word_set ) }
    nodes = [ {'word':word} for word in word_set ]
    relations = []

    for from_word, edges in d.items():
        for to_word, p in edges.items():
            relations.append( ( idx[from_word], "ADJACENCY", idx[to_word], {"Probability": p} ) )

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
        p = rel._properties['Probability']

        if start in d.keys():
            d[ start ][ end ] = p
        else:
            d[ start ] = { end: p }

    return d