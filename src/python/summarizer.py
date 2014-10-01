from nltk.corpus import wordnet as wn
import re, requests, json, random

wiki_stem = 'https://en.wikipedia.org/wiki/'

def get_html(topic):
	return requests.get('%s%s' % (wiki_stem,topic)).text	

def get_paragraphs(topic):
	html = get_html(topic)
	pattern = '<p>.+?</p>'
	try:
		paragraphs = [remove_html_tags(match) for match in re.findall(pattern, html)]
		return paragraphs
	except:
		return None

def remove_html_tags(text):
	text = re.sub('<[^>]*>', '', text)
	return text

def build_idea_tree(topic):
	try:
		synset   = wn.synsets(topic)[0]
	except:
		return None
	path     = synset.hypernym_paths()[0]
	root     = {}
	child    = root
	parent   = None
	for item in path:
		print(item)
		child['name']       = item.lemma_names()[0]
		child['definition'] = item.definition()
		child['paragraphs'] = get_paragraphs(child['name'])
		child['children']	= []

		for i in range(0, 4):
			if i < len(item.hyponyms()):
				hyponym         = {}
				hyponym['name'] = item.hyponyms()[i].lemma_names()[0]
				hyponym['definition'] = item.hyponyms()[i].definition()
				hyponym['size'] = len(hyponym['name'])
				hyponym['paragraphs'] = get_paragraphs(hyponym['name'])
				child['children'].append(hyponym)

		if item != path[0]:
			parent['children'].append(child)
		if item == path[-1]:
			child['size'] = len(child['name'])
		parent = child
		child  = {}

	return root

'''		
		for hyponym in item.hyponyms()[:5]:
			print('\t%s' % hyponym)
			child               = {}
			child['name']       = hyponym.lemma_names()[0]
			child['size']       = int(random.random()*1000)
			child['paragraphs'] = get_paragraphs(child['name'])
			parent['children'].append(child)
'''

if __name__ == "__main__":
	flare2 = open('./flare2.json', 'w')
	idea_tree = build_idea_tree('biochemistry')
	print(idea_tree)
	json.dump(idea_tree, flare2)
	flare2.close()
#print json.dumps(build_idea_tree('truck'),indent=4, separators=(',',':'))
#print(get_html('truck'))


'''
html = requests.get('https://en.wikipedia.org/wiki/Computer').text
for i in range(0, 5):
	print ('\n %s' % get_paragraph_by_index(html, i))
'''
