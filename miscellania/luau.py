# luau.py
# Contact: Jacob Schreiber
#          jmschreiber91@gmail.com

'''
Read a book and build a POS HMM. This uses the NLTK tagged word corpora, and
attempts to reverse-engineer the nltk POS HMM, since it isn't provided.

Model-building is done by crude viterbi training, which builds emissions and 
transitions based solely on observations of the book.

This will build a model by reading a book, and generate sentences off of it
for your amusement.

Requirement: yahmm, nltk, numpy
Find at: www.github.com/jmschrei/yahmm
'''

import nltk
from nltk.corpus import gutenberg
import numpy as np
from yahmm import *

def tagged_sentences( book ):
	'''
	Generator yielding one sentence at a time, filtering out the -NONE- tagged
	sentences, which are anomalies in the words.
	'''

	for sentence in gutenberg.sents( book ):
		yield filter( lambda x: x[1] not in [':', '-NONE-', ], nltk.pos_tag( sentence ) )


# Begin by building up a dictionary of transitions and emissions, and some
# statistics gathering variables.
emissions, transitions = {}, {} 
starts = collections.defaultdict( float )
ends =  collections.defaultdict( float )
n_sentences, n_words = 0, 0

# Go through every book and assign the emissions and transitions as-seen in the
# observations, as tagged by the nltk POS HMM tagger.
for book in ['shakespeare-hamlet.txt']: #gutenberg.fileids():
	for sentence in tagged_sentences( book ):
		n_sentences += 1
		n_words += len( sentence ) - 1 
		if len( sentence ) == 0:
			continue

		for word, tag in sentence:
			if tag in emissions:
				if word in emissions[ tag ]:
					emissions[ tag ][ word ] += 1
				else:
					emissions[ tag ][ word ] = 1
			else:
				emissions[ tag ] = { word: 1 }

		for (word, pos), (next_word, next_pos) in zip( sentence[:-1], sentence[1:] ):
			if pos in transitions:
				if next_pos in transitions[ pos ]:
					transitions[ pos ][ next_pos ] += 1
				else:
					transitions[ pos ][ next_pos ] = 1
			else:
				transitions[ pos ] = { next_pos: 1 }

		starts[ sentence[0][1] ] += 1
		ends[ sentence[-1][1] ] += 1

# Normalize the values from counts into probabilities before adding them
norm = sum( starts.values() ) * 1.
starts = { key: value / norm for key, value in starts.items() }

# Normalize the emissions as well
for key in emissions.keys():
	norm = sum( emissions[key].values() )
	emissions[key] = { k: 1.* v / norm for k, v in emissions[key].items() }

# Create the model and state objects for the HMM.
model = Model( name='luau' )
states = { pos: State( DiscreteDistribution( dist ) ) for pos, dist in emissions.items() }

for state in states.values():
	model.add_state( state )
	
for pos in transitions.keys():
	norm = sum( transitions[pos].values() ) * 1. + ( ends[pos] if pos in ends else 0 )
	transitions[pos] = { key: value / norm for key, value in transitions[pos].items() }
	if pos in ends:
		model.add_transition( states[pos], model.end, ends[pos] / norm ) 
	for next_pos in transitions[pos].keys():
		model.add_transition( states[pos], states[next_pos], transitions[pos][next_pos] )

for pos, prob in starts.items():
	model.add_transition( model.start, states[pos], prob )

model.bake( verbose=True )

# Give a quick summary of the model.
print "Model-Building Complete!"
print "Summary:"
print "\tTrained on {} sentences, comprising {} words".format( n_sentences, n_words )
print "\t{} edges formed between {} nodes".format( len( model.graph.edges() ), len( states ) )
print

# Generate sentences until the user is satisfied.
while True:
	sentence = ' '.join( model.sample() )
	print sentence[0].upper() + sentence[1:]
	print
	raw_input(">>> Click 'Enter' for next.")
	print