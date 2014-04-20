#!/usr/bin/env python


import nltk, zipfile, argparse

from boilerpipe.extract import Extractor

###############################################################################
## Utility Functions ##########################################################
###############################################################################

def get_tagged_words(raw_documents):
    sentences = [nltk.sent_tokenize(raw_text) for raw_text in raw_documents]
    # a list of documents -> a list of sentences -> a list of tokenized words
    words = []
    # a list of documents -> a list of sentences -> a list of POS tagged words
    tags = []

    # tokenize the words    
    for document in sentences:
        doc_sentences = []
        # for each sentence (i.e., a string)
        for sentence in document:
            # tokenize the words (an array of tokens)
            sentence_words = nltk.word_tokenize(sentence)
            # add them to a list representing the sentences 
            doc_sentences.append(sentence_words)
        # add the word tokenized sentences to the document
        words.append(doc_sentences)

    for document in words:
        doc_tags = []
        for sentence in document:
            sentence_tags = nltk.pos_tag(sentence)
            doc_tags.append(sentence_tags)
        tags.append(doc_tags)

    return tags
    #words = [nltk.word_tokenize(sent) for doc in sentences for sent in doc]
    #tagged_words = [nltk.pos_tag(sent) for sent in words]
    #return tagged_words
    #return [tagged_word for sent in tagged_words for tagged_word in sent]

def generate_model(cfdist, word, num=15):
    print "conditionally generating {0} words:".format(num),
    for i in xrange(num):
        print word,
        word = cfdist[word].max()
    print ""
    
def write_tags(corpus_name, tagged_words):
    fh = open("{0}-pos.txt".format(corpus_name), "w")
    
    for document in tagged_words:
        for sentence in document:
            fh.write(u" ".join(u"{0}/{1}".format(*t) for t in sentence).encode('utf-8'))
            fh.write('\n')
        fh.write('\n')
    fh.close()
    
def write_word_freq(fdist, corpus_name):
    fh = open("{0}-word-freq.txt".format(corpus_name), "w")
    
    for word, freq in fdist.iteritems():
        fh.write(u"{0:30s} {1:5d}\n".format(word, freq).encode('utf-8'))
    fh.close()
    
def write_pos_cfd(cfdist, corpus_name, vocabulary):
    fh = open("{0}-pos-word-freq.txt".format(corpus_name), "w")
    
    fh.write("POS\t")
    fh.write(u"\t".join(vocabulary).encode("utf-8"))
    fh.write("\n")
    for condition in cfdist.conditions():
        fdist = cfdist[condition]
        fh.write("{0:s}\t".format(condition))
        #print condition, 
        for word in vocabulary:
            count = fdist.get(word, 0)
            
            #print count,
            fh.write(str(count) + "\t") 
        fh.write("\n")
    
    fh.close()

def process_corpus(raw_documents, corpus_name):
    print "There are", len(raw_documents), "documents in the corpus"
    
    tagged_words = get_tagged_words(raw_documents)
    write_tags(corpus_name, tagged_words)
    
    tags = []
    words = []
    tagged_words_flat = []
    vocabulary = set()
    for document in tagged_words:
        for sentence in document:
            for token in sentence:
                words.append(token[0].lower())
                vocabulary.add(token[0].lower())
                tagged_words_flat.append((token[1], token[0].lower().encode('utf-8')))
                tags.append(token[1])
    
    fdist = nltk.FreqDist(words)
    pfdist = nltk.FreqDist(tags)
    write_word_freq(fdist, corpus_name)
    
    cfdist = nltk.ConditionalFreqDist(tagged_words_flat)
    
    write_pos_cfd(cfdist, corpus_name, vocabulary)
    
    text = nltk.Text(words)
    for pos in ["NN", "VBD", "JJ", "RB"]:
        word = cfdist[pos].max()
        print "most similar words to '{0}' for part of speech '{1}' are:".format(word, pos)
        text.similar(word)
        
    text.collocations()
    print "# of tokens: {0}".format(len(words))
    print "Vocab size: {0}".format(fdist.B())
    print "Most frequent POS: {0} with freq: {1}".format(pfdist.max(), pfdist[pfdist.max()])
        
###############################################################################
## Stub Functions #############################################################
###############################################################################
def process_fables(input_file):
    # They would fill this code in
    fables_zip = zipfile.ZipFile(input_file, 'r')
    raw_documents = [fables_zip.open(fn, "rU").read() for fn in fables_zip.namelist() if fn.endswith(".txt")]
    
    process_corpus(raw_documents, "fables")
    
def process_blogs(input_file):
    # They would fill this code in
    blogs_zip = zipfile.ZipFile(input_file)

    print "\n".join([fn for fn in blogs_zip.namelist()])
    file_names = [fn for fn in blogs_zip.namelist()]
    for filename in file_names:
        fh = blogs_zip.open(filename, "rU")
        raw_text = fh.read()
        print raw_text

    urls = [blogs_zip.open(fn, "rU").read().split() for fn in blogs_zip.namelist() if fn.endswith(".txt")]
    #for category in urls:
    #    for url in category:
    #        print category, url
    raw_documents = [
        Extractor(extractor="LargestContentExtractor", url=url).getText()
        for category in urls
        for url in category
    ]
    
    process_corpus(raw_documents, "blogs")
    #print u"\n\n".join(raw_documents).encode("utf-8") 

###############################################################################
## Program Entry Point ########################################################
###############################################################################
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Assignment 1')
    parser.add_argument('--corpus', required=True, dest="corpus", metavar='NAME',  help='Which corpus to process {fables, blogs}')
    parser.add_argument('--input-file', dest='input_file', metavar='FILE', help='The path to the input file')

    args = parser.parse_args()
    
    corpus_name = args.corpus
    input_file = args.input_file
    
    if corpus_name == "fables":
        process_fables(input_file)
    elif corpus_name == "blogs":
        process_blogs(input_file)
    else:
        print "Unknown corpus name: {0}".format(corpus_name)