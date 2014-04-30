import nltk
import re


def remove_tiny_sentences(sentences):
	digrx = re.compile('.*\\d.*')
	for i in range(0,len(sentences)):
		try:
			sentence = sentences[i]
		except:
			pass
		
		words = nltk.word_tokenize(sentence)
		if len(words)<3:
			sentences.remove(sentence)
			continue

		for word in words:
			if re.match(digrx, word) != None:
				words.remove(word)
				#print 'removing word: '+word

		newSentence = ''
		for word in words:
			newSentence += word.lower() + ' '
		try:
			sentences[i] = newSentence
		except:
			pass
	return sentences

def remove_urls(text):
	res = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
	if len(res) > 0:
		print res
	text = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text, re.S)
	return text

def same_sentence_frequency(sentences):
	frequency_matrix = {}

	# for each sentence
	for sentence in sentences:
		# tokenize the sentence
		words = nltk.word_tokenize(sentence)

		# for each word in the sentence
		for word1 in words:
			if not frequency_matrix.has_key(word1):
				frequency_matrix[word1] = {}

			# increment frequency for each other word in sentence
			for word2 in words:
				if word2 != word1:
					if not frequency_matrix[word1].has_key(word2):
						frequency_matrix[word1][word2] = 1
					else:
						frequency_matrix[word1][word2] = frequency_matrix[word1][word2] + 1

	return frequency_matrix				


with open( '/Users/ganesha/Code/Poetry/doc/texts/Bitcoin.txt', 'r' ) as infile:
	text = ''
	for line in infile:
		text += line

text = remove_urls(text)
sentences = nltk.sent_tokenize(text)
sentences = remove_tiny_sentences(sentences)
print sentences

freq_mat = same_sentence_frequency(sentences)

print freq_mat

