import nltk
import re
import poetry_neo
import os
import time
import collections

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
			#print 'removing short sentence : ' + sentence
			continue

		# remove words with numbers in them and punctuation
		cleaned_words = []
		for word in words:
			if re.match(digrx, word) == None:	
				if len(word) > 1 or word.lower() == 'i' \
				or word.lower() == 'a' or word.lower() == 'o':
					cleaned_words.append(word)
				else:
					pass
					#print 'removing word: ' + word

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

def normalize_same_sentence_frequency_matrix_symmetric(freqMat):
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

def normalize_same_sentence_frequency_matrix_asymmetric(freqMat):
	normedFreqMat = {}

	# for each pair of words encountered
	for word1 in freqMat.keys():
		if not normedFreqMat.has_key(word1):
			normedFreqMat[word1] = {} 
		for word2 in freqMat.keys():
			if freqMat[word1].has_key(word2):
				# divide frequency by the frequency of word2
				# given that you saw word2, what's the probability of seeing word1?
				normedFreqMat[word1][word2] = float(freqMat[word1][word2]) / freqMat[word2][word2]

	return normedFreqMat		

def get_all_sentences(path_to_texts):
	sentences = []
	for filename in os.listdir(path_to_texts):
		text = ''
		print filename
		with open( path_to_texts + filename) as file:
			for line in file:
				text += line
		sentences += cleaned_sentences_from_text(text)
	return sentences

def remove_words_below_threshold(freqMat, threshold):
	words_to_remove = []

	for word in freqMat.keys():
		if freqMat[word][word] < threshold:
			print 'removing infrequent word: ', word
			words_to_remove.append(word)

	for word1 in freqMat.keys():
		if word1 in words_to_remove:
			del freqMat[word1]
		else: 
			for word2 in freqMat[word1].keys():
				if word2 in words_to_remove:
					del freqMat[word1][word2]

	return freqMat

def print_words_with_frequency(freqMat):
	for word in freqMat.keys():
		print word + ',' + str(freqMat[word][word])

def calculate_frequency_mean(freqMat):
	means = {}

	for word1 in freqMat.keys():
		mean = 0
		for word2 in freqMat[word1].keys():
			mean += float(freqMat[word1][word2])

		mean /= len(freqMat[word1])
		means[word1] = mean

	return means

def calculate_frequency_variance(freqMat):
	means = calculate_frequency_mean(freqMat)

	variances = {}

	for word1 in freqMat.keys():
		variance = 0
		for word2 in freqMat[word1].keys():
			variance += (float(freqMat[word1][word2]) - float(means[word1])) ** 2

		variance /= float(len(freqMat[word1]))
		variances[word1] = variance

	return variances

##############################################################################
linebreak = "\n\n\n#######################################################################\n\n\n"


sentences = get_all_sentences('../../doc/texts/')
#sentences = get_all_sentences('../../doc/test_texts/')

start_time = time.time()
freq_mat = same_sentence_frequency_matrix(sentences)
end_time = time.time()
print 'frequency matrix: ' + str(freq_mat)
print 'took ' + str(end_time - start_time) + ' seconds to compute'

print linebreak

print_words_with_frequency(freq_mat)


asymmetric_normed_freq_mat = normalize_same_sentence_frequency_matrix_asymmetric(freq_mat)
var_mat = calculate_frequency_variance(asymmetric_normed_freq_mat)
sorted_normed = collections.OrderedDict(sorted(var_mat.items(), key=lambda t:t[1]))

var_file = open('var_file', 'w')
var_file.write(str(sorted_normed))
var_file.close()

#freq_map = word_frequency_per_sentence(sentences)
#print 'frequency map: ' + str(freq_map)

print linebreak
os.system("say 'done'")
'''
symmetric_normed_freq_mat = normalize_same_sentence_frequency_matrix_symmetric(freq_mat)
print 'symmetric normed frequency matrix: ' + str(symmetric_normed_freq_mat)

print linebreak

asymmetric_normed_freq_mat = normalize_same_sentence_frequency_matrix_asymmetric(freq_mat)
print 'asymmetric normed frequency matrix: ' + str(asymmetric_normed_freq_mat)


#poetry_neo.persist_graph(normed_freq_mat)
poetry_neo.graph_push(symmetric_normed_freq_mat)
'''
