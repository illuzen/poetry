# keledones.py
# Contact: Jacob Schreiber
#          jmschreiber91@gmail.com

"""
Objects which will help standardize natural language processing.
"""

import nltk
import re
import glob, os
import collections

class Document( object ):
	"""
	A wrapper class for a single text. An example is a book, or a proposal.
	"""

	def __init__( self, text, stop_words=None ):
		"""
		Assume that the text given is a string, and filter out stop words if
		given.
		"""

		self.text = text
		if stop_words:
			self.filter( stop_words )

	def filter( self, stop_words ):
		"""
		Filter the text by removing all of the stop words from the text. This
		is usually done to remove common words that add nothing to the text.
		"""

		stop_words = set( stop_words )
		self.text = ' '.join( word for word in self.text 
			if word not in stop_words )

	def apply_regex( self, regex, *args ):
		"""
		Apply a regex to the text and return it. 
		"""

		pattern = re.compile( regex, *args )
		return re.findall( pattern, self.text )

	def tokenize( self ):
		"""
		Return the tokens of the text, as specified by nltk.
		"""

		return nltk.word_tokenize( self.text )

	def sentences( self ):
		"""
		A generator which yields sentences one at a time. This may be a bad
		idea if there is formatting at the beginning of the document.
		"""

		for sentence in self.text.split("."):
			yield sentence + "." 

	def pairwise_dictionary( self, normalize=False ):
		"""
		Builds off of the sentence generator, by building a pairwise dictionary
		off of adjacent words in each sentence.
		"""

		d = {}
		for sentence in self.sentences():
			sentence = sentence.replace( ",", "" ).lower().split()

			for word, adj_word in zip( sentence[:-1], sentence[1:] ):
				if word in d:
					if adj_word in d[word]:
						d[word][adj_word] += 1
					else:
						d[word][adj_word] = 1
				else:
					d[word] = { adj_word: 1 }

		if normalize:
			for word, adj_words in d.items():
				edge_sum = float( sum( d[word].values() ) )
				d[word] = { adj_word: count / edge_sum \
					for adj_word, count in d[word].items() }

		return d

	def word_count( self, normalize=False ):
		"""
		Return a dictionary of the word count of the document. If you choose to
		normalize it, this will be probabilities and not counts. This uses the
		nltk tokenizer, and filters out punctuation.
		"""

		stop = set(', . < > / ? : ; \' \" { [ } ] - _ + = | \ ! @ # $ % ^ & * `'.split() )
		d = collections.defaultdict( float )
		
		for token in self.tokenize():
			if token in stop:
				continue
			else:
				d[ token ] += 1

		if normalize:
			document_length = float( sum( d.values() ) )
			for token, count in d.items():
				d[token] = count / document_length

		return d

	def compare( self, word_count ):
		"""
		This function will take in the word count dictionary from another
		document, and return a dictionary of the number of times a word from
		the other document appears in this document.
		"""

		self_word_count = self.word_count()
		similarity = {}

		for token, count in word_count.items():
			if token in self_word_count.keys():
				similarity[token] = self_word_count[token]

		return similarity

	@classmethod
	def from_txt( cls, filename ):
		"""
		Open a raw text file and save that as the text.
		"""

		with open( filename, "r" ) as infile:
			return cls( ''.join( line.strip("\r\n") for line in infile ) )

class Corpus( object ):
	"""
	A collection of documents. This is to make handling of large scale NLP
	operations easier.
	"""

	def __init__( self, documents ):
		"""
		Store the documents, and assert they are all correct.
		"""

		assert all( isinstance(document, Document) for document in documents )
		self.documents = documents

	def pairwise_dictionary( self, normalize=False ):
		"""
		A wrapper for the pairwise_dictionary function on a document, but
		applied to all documents in the corpus.
		"""

		corpus_pairwise = {}
		for document in self.documents:
			d = document.pairwise_dictionary()

			for word, adj_words in d.items():
				for adj_word, count in adj_words.items():
					if word in corpus_pairwise:
						if adj_word in corpus_pairwise[word]:
							corpus_pairwise[word][adj_word] += count
						else:
							corpus_pairwise[word][adj_word] = count
					else:
						corpus_pairwise[word] = { adj_word: count }

		if normalize:
			for word, adj_words in d.items():
				edge_sum = float( sum( d[word].values() ) )
				d[word] = { adj_word: count / edge_sum \
					for adj_word, count in d[word].items() }

		return corpus_pairwise

	def filter( self, stop_words ):
		"""
		Filter an entire corpus by a set of stop words, removing them from
		every document.
		"""

		for document in self.documents:
			document.filter( stop_words )

	def tokenize( self ):
		"""
		Return the tokens in each document, as specified by nltk.
		"""

		return [ document.tokenize() for document in self.documents ]

	def sentences( self ):
		"""
		Yield each sentence in each document, going through the entire corpus.
		"""

		for document in self.documents:
			for sentence in document.sentences():
				yield sentence

	def word_count( self, normalize=False ):
		"""
		Return the word count of the entire corpus, by gettig the word count of
		each document one at a time.
		"""

		d = collections.defaultdict( float )

		for document in self.documents:
			for token, count in document.word_count().items():
				d[token] += count

		if normalize:
			corpus_length = float( sum( d.values() ) )
			for token, count in d.items():
				d[token] = count / corpus_length

		return d


	@classmethod
	def from_folder( cls, path  ):
		"""
		Create a corpus from a set of text documents in a folder. Give the
		absolute path of the folder, and it will select out the txt files.
		"""

		documents = []
		for filename in glob.glob( os.path.join( path, '*.txt') ):
			document = Document.from_txt( filename )
			documents.append( document )
		return cls( documents )