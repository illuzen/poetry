import nltk
import re
import poetry_neo
import os

def cleaned_sentences_from_text(text):
	text_without_urls = remove_urls_from_text(text)
	sentences = nltk.sent_tokenize(text)
	cleaned_sentences = clean_sentences(sentences)
	return cleaned_sentences

def clean_sentences(sentences):
	new_sentences = []
	digrx = re.compile('.*\\d.*')
	for sentence in sentences:
		words = nltk.word_tokenize(sentence)

		# remove short sentences
		if len(words)<3:
			print 'removing short sentence : ' + sentence
			continue

		# remove words with numbers in them and punctuation
		cleaned_words = []
		for word in words:
			if re.match(digrx, word) == None:	
				if len(word) > 1 or word.lower() == 'i' \
				or word.lower() == 'a' or word.lower() == 'o':
					cleaned_words.append(word)
				else:
					print 'removing word: ' + word

		# reconstruct sentences
		newSentence = ''
		for word in cleaned_words:
			newSentence += word.lower() + ' '
		
		new_sentences.append(newSentence)
	return new_sentences

def remove_urls_from_text(text):
	'''
	res = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
	if len(res) > 0:
		print res
	'''
	text = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text, re.S)
	return text

def same_sentence_frequency_matrix(sentences):
	frequency_matrix = {}

	# for each sentence
	for sentence in sentences:
		# tokenize the sentence
		words = nltk.word_tokenize(sentence)

		seen_it = []
		# for each word in the sentence
		for word1 in words:
			seen_it_2 = []

			if word1 not in seen_it:
				seen_it.append(word1)
				if not frequency_matrix.has_key(word1):
					frequency_matrix[word1] = {}
				# increment frequency for each other word in sentence
				for word2 in words:
					if word2 not in seen_it_2:
						seen_it_2.append(word2)
						if not frequency_matrix[word1].has_key(word2):
							frequency_matrix[word1][word2] = 1
						else:
							frequency_matrix[word1][word2] += 1

	return frequency_matrix				

def word_frequency_per_sentence(sentences):
	frequency_map = {}

	for sentence in sentences:
		words = nltk.word_tokenize(sentence)
		seen_it = []
		for word in words:
			if not word in seen_it:
				seen_it.append(word)
				if not frequency_map.has_key(word):
					frequency_map[word] = 1
				else:
					frequency_map[word] = frequency_map[word] + 1

	return frequency_map

def normalize_same_sentence_frequency_matrix(freqMat):
	normedFreqMat = {}
	# for each pair of words encountered
	for word1 in freqMat.keys():
		if not normedFreqMat.has_key(word1):
			normedFreqMat[word1] = {} 
		for word2 in freqMat.keys():
			if freqMat[word1].has_key(word2):
				# divide frequency by the frequency of (word1 union word2)
				# given that you saw one of them, what's the probability of seeing the other one?
				normedFreqMat[word1][word2] = float(freqMat[word1][word2]) / (freqMat[word1][word1] + freqMat[word2][word2] - freqMat[word1][word2])

	return normedFreqMat

def get_all_sentences(path_to_texts):
	sentences = []
	for filename in os.listdir(path_to_texts):
		text = ''
		print filename
		with open( path_to_texts + filename) as file:
			for line in file:
				text += line
		sentences.append(cleaned_sentences_from_text(text))
	return sentences

sentences = get_all_sentences('../../doc/texts/')

freq_mat = same_sentence_frequency_matrix(sentences)
print 'frequency matrix: ' + str(freq_mat)

freq_map = word_frequency_per_sentence(sentences)
print 'frequency map: ' + str(freq_map)

normed_freq_mat = normalize_same_sentence_frequency_matrix(freq_mat)
print 'normed frequency matrix: ' + str(normed_freq_mat)

#poetry_neo.persist_graph(normed_freq_mat)
poetry_neo.graph_push(normed_freq_mat)
new_mat = poetry_neo.graph_pull()
print new_mat

