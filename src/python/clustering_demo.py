import os, re, sys, nltk
from py2neo import neo4j, node, rel


kWIKI_PAGE_DIRECTORY = './Bitcoin/'
kNUM_CLUSTERS = 5

class Wiki_Page:
	def __init__(self, title, html, keyword_frequencies):
		self.title               = title
		self.html                = html
		self.keyword_frequencies = keyword_frequencies
		self.neighbors			 = set()

	def __str__(self):
		return self.title
	

class Hierarchical_Cluster:
	def __init__(self, wiki_pages):
		self.children  = wiki_pages
		self.neighbors = set.union(*[wiki_page.neighbors for wiki_page in wiki_pages])

	def merge(self, other):
		merged_children = set(self.children) | set(other.children)
		return Hierarchical_Cluster(merged_children)

	def distance_to(self, other):
		distance_sum = 0
		for self_child in self.children:
			for other_child in other.children:
				distance_sum += get_L2_keyword_distance_pair(self_child.keyword_frequencies, \
															other_child.keyword_frequencies)
		distance_sum /= (len(self.children) * len(other.children))
		return distance_sum

	def connects_to(self, other):
		other_titles = [child.title for child in other.children]
		return len(set(self.neighbors) & set(other_titles)) > 0

	def title(self):
		return ' '.join(map(lambda item: item[0], get_most_frequent_words(self, 5)))

	def __str__(self):
		return str(self.children)


wiki_url_stem = '.*/wiki/'
link_tag_stem = '<a href=\"'
function_words = ['be', 'is', 'did', 'able', 'to', 'can', 'could', 'dare', 'had', 
				'have', 'may', 'might', 'must', 'need', 'ought', 'shall', 'should', 
				'used', 'will', 'would', 'accordingly', 'after', 'at', 'was', 'albeit',
				'although', 'and', 'as', 'because', 'before', 'both', 'but', 
				'either', 'with','for', 'hence', 'however', 'if', 'neither', 
				'of', 'in', 'nor', 'once', 'or', 'since', 'by', 'are', 'so', 'not',  
				'than', 'that', 'then', 'thence', 'therefore', 'tho', 'though', 'thus', 
				'from', 'unless', 'until', 'when', 'whenever', 'where', 'whereas', 
				'wherever', 'whether', 'while', 'whilst', 'on', 'were', 'yet', 'a', 
				'an', 'another', 'any', 'both', 'each', 'either', 'every', 'her', 'his', 
				'its', 'my', 'neither', 'no', 'other', 'our', 'per', 'some', 'the', 
				'their', 'these', 'this', 'those', 'whatever', 'whichever', 'your',
				'all', 'another', 'any', 'anybody', 'anyone', 'anything', 'both', 'each', 
				'either', 'everybody', 'everyone', 'everything', 'few', 'he', 'her',  
				'herself', 'him', 'himself', 'his', 'I', 'it', 'itself', 'many', 'into',
				'me', 'mine', 'myself', 'neither', 'nobody', 'none', 'nothing', 'one',  
				'ours', 'ourselves', 'several', 'she', 'some', 'somebody', 'someone', 
				'something', 'such', 'theirs', 'them', 'themselves', 'these', 'they', 
				'we', 'what', 'which', 'whichever', 'you', 'whose', 'who', 'whom', 
				'whomever', 'whose', 'yours', 'yourself', 'yourselves', 'all', 'another', 
				'any', 'both', 'certain', 'each', 'either', 'enough', 'few', 'fewer', 
				'less', 'little', 'loads', 'lots','many', 'more', 'most', 'much', 
				'none', 'part', 'plenty', 'quantities', 'several', 'some','various', 
				'also', 'till', 'other', 'consequently','hers','nevertheless','us',
				'neither','has', 'out', 'all', 'edit' ]


def get_wiki_pages(path_to_wiki_pages):
	wiki_dir   = os.listdir(path_to_wiki_pages)
	num_pages  = len(wiki_dir)
	wiki_pages = []
	for page_index in range(0, num_pages):
		page_name = wiki_dir[page_index].lower()
		#print (page_name)
		with open(path_to_wiki_pages + page_name, 'r') as page:
			html = page.read()
			wiki_pages.append(Wiki_Page(page_name, html, get_keyword_frequency(html)))
	get_neighbors(wiki_pages)
	return wiki_pages

def get_neighbors(wiki_pages):
	wiki_titles = [wiki_page.title for wiki_page in wiki_pages]
#	print ('wiki_titles %s' % wiki_titles)
	for wiki_page in wiki_pages:
		print (wiki_page.title)
#		pattern = '%s%s[^\"]*\"' % (link_tag_stem, wiki_url_stem)
		pattern = '<a href=\"[^\"]*?/wiki/[^\"]*?\"'
		matches = re.findall(pattern, wiki_page.html, re.DOTALL)
		for match in matches:
			dest_name = ('%s' % match[match.rfind('/') + 1:-1]).lower()
#			print ('dest_name %s' % dest_name)
			if dest_name in wiki_titles and dest_name not in wiki_page.neighbors \
				and dest_name != wiki_page.title:
				print ('\t%s' % dest_name)
				wiki_page.neighbors.add(dest_name)

def get_most_frequent_words(cluster, num_words):
	key_freqs = [child.keyword_frequencies for child in cluster.children]
	master_key_freq = merge_keyword_frequencies(key_freqs)
	sorted_by_freq  = sorted(master_key_freq.items(), key=lambda freq: freq[1])
	#print ('sorted by freq %s' % sorted_by_freq)
	return sorted_by_freq[-num_words:]

def get_keyword_frequency(text):
	keyword_freq = {}
	text   = remove_scripts(text)
	text   = remove_html_tags(text)
	text   = re.sub('[^\x00-\x7F]+',' ', text)
	words  = nltk.word_tokenize(text)
	wordrx = re.compile('[a-zA-Z\-]*[a-zA-Z,.]$')
 
	for word in words:
		word = word.lower()
		if re.match(wordrx, word) and word not in function_words:
			word = re.sub('[.,]', '', word)
			if len(word) < 2:
				continue
#			print ('keeping %s' % word)
			try:
				keyword_freq[word] += 1
			except:
				keyword_freq[word] = 1				
		else:
#			print ('removing %s' % word)
			continue
	return keyword_freq

def merge_keyword_frequencies(keyword_frequencies):
	master_key_freq = {}
	for keyword_frequency in keyword_frequencies:
		for keyword in keyword_frequency.keys():
			try:
				master_key_freq[keyword] += keyword_frequency[keyword]
			except:
				master_key_freq[keyword] = keyword_frequency[keyword]
	return master_key_freq

def remove_scripts(text):
#	scripts = re.findall('<script.*?</script>', text, flags=re.DOTALL)
#	print scripts
	text = re.sub('<script.*?</script>', '', text, flags=re.DOTALL)
	return text

def remove_html_tags(text):
#	tags = re.findall('<[^>]*>', text)
#	print (tags)
	text = re.sub('<[^>]*>', '', text)
	return text

def get_L2_keyword_distance_pair(keyword_frequency_1, keyword_frequency_2):
	# get union of keys
	keys = list(set(keyword_frequency_1.keys()) | set(keyword_frequency_2.keys()))

	square_sum = 0
	for keyword in keys:
		if keyword not in keyword_frequency_1.keys():
			square_sum += keyword_frequency_2[keyword] ** 2	
		elif keyword not in keyword_frequency_2.keys():
			square_sum += keyword_frequency_1[keyword] ** 2	
		else:
			square_sum += (keyword_frequency_1[keyword] - \
						   keyword_frequency_2[keyword]) ** 2

	return square_sum

def hierarchical_clustering(wiki_pages, max_clusters):
	clusters = [Hierarchical_Cluster([wiki_page]) for wiki_page in wiki_pages]
	while len(clusters) > max_clusters:
		print('len(clusters): %s max_clusters: %s' % (len(clusters), max_clusters))
		new_clusters = []
		num_clusters = len(clusters)
		already_clustered_idxs = []
		for i in range(0,num_clusters):
			print('\t%d' % i)
			if i in already_clustered_idxs:
				continue

			cluster_i        = clusters[i]
			min_distance     = float('inf')
			min_distance_idx = -1
			for j in range(i + 1, num_clusters):
				print('\t\t%d' % j)
				if j in already_clustered_idxs:
					continue

				cluster_j    = clusters[j]
				dist_between = cluster_i.distance_to(cluster_j)
				if dist_between < min_distance and \
					True:
#					cluster_i.connects_to(cluster_j):
					min_distance_idx = j
					min_distance     = dist_between
			
			if min_distance_idx == -1:
				new_clusters.append(cluster_i)
				already_clustered_idxs.append(i)
				continue

			new_cluster = cluster_i.merge(clusters[min_distance_idx])
			new_clusters.append(new_cluster)
			already_clustered_idxs.append(i)
			already_clustered_idxs.append(min_distance_idx)
			#print('already_clustered_idxs %s' % already_clustered_idxs)
		clusters = new_clusters
	return clusters

def print_clusters(clusters):
	for cluster in clusters:
		print(cluster.title())
		for child in cluster.children:
			print(child)
		print('\n')

def graph_clusters(clusters):
	graph_db = neo4j.GraphDatabaseService('http://localhost:7474/db/data/')
	nodes = [node(title=cluster.title(), pages=[child.title for child in cluster.children]) \
															for cluster in clusters]
	relations = []
	num_clusters = len(clusters)
	for i in range(0, num_clusters):
		for j in range(i + 1, num_clusters):
			if clusters[i].connects_to(clusters[j]):
				print('%s connects to %s' % (clusters[i].title(), clusters[j].title()))
				relations.append(rel(i, 'LINKS TO', j))
#			if clusters[j].connects_to(clusters[i]):
#				relations.append(rel(j, 'LINKS TO', i))

	graph_db.create(*(nodes + relations))
#	graph_db.create(*relations)	


wiki_pages = get_wiki_pages(kWIKI_PAGE_DIRECTORY)
clusters = hierarchical_clustering(wiki_pages, kNUM_CLUSTERS)
print_clusters(clusters)
graph_clusters(clusters)
'''
def get_L2_keyword_distance(keyword_frequencies):
	dist_mat = {}

	for kf_index_1 in range(0, len(keyword_frequencies)):
		keyword_frequency_1 = keyword_frequencies[kf_index_1]
		source_1 = keyword_frequency_1['__source']
		try:
			dist_mat[source_1][source_1] = 0
		except:
			dist_mat[source_1] = {}
			dist_mat[source_1][source_1] = 0

		for kf_index_2 in range(kf_index_1 + 1, len(keyword_frequencies)):
			keyword_frequency_2 = keyword_frequencies[kf_index_2]
			source_2 = keyword_frequency_2['__source']

			square_sum = get_L2_keyword_distance_pair(keyword_frequency_1, keyword_frequency_2)

			print('source_1 %s source_2 %s' % (source_1,source_2))
			dist_mat[source_1][source_2] = square_sum ** 0.5
			try:
				dist_mat[source_2][source_1] = dist_mat[source_1][source_2]
			except:
				dist_mat[source_2] = {}
				dist_mat[source_2][source_1] = dist_mat[source_1][source_2]

			dist_mat[source_2][source_2] = 0

	return dist_mat

def merge_keyword_frequencies(keyword_frequencies):
	master_key_freq = {}
	for keyword_frequency in keyword_frequencies:
		for keyword in keyword_frequency.keys():
			try:
				master_key_freq[keyword] += keyword_frequency[keyword]
			except:
				master_key_freq[keyword] = keyword_frequency[keyword]
	return master_key_freq


def get_adjacency_matrix(path_to_wiki_pages):
	wiki_dir = os.listdir(path_to_wiki_pages)
	num_pages = len(wiki_dir)
	adj_mat = [[0 for i in range(0, num_pages)] for i in range(0, num_pages)]	
	for i in range(0, num_pages):
		filename = wiki_dir[i]
		print (filename[:-5])
		with open(path_to_wiki_pages + filename) as file:
			pattern = '%s%s[^\":#]*\"' % (link_tag_stem, wiki_url_stem)
			matches = re.findall(pattern, file.read())
			for match in matches:
				dest_name = '%s.html' % match[match.rfind('/') + 1:-1]
				if dest_name in wiki_dir:
					print ('\t%s (%s,%s)' % (dest_name, wiki_dir[i], \
									wiki_dir[wiki_dir.index(dest_name)]))
					adj_mat[i][wiki_dir.index(dest_name)] = 1

	return adj_mat

def get_keyword_frequencies(path_to_wiki_pages):
	wiki_dir = os.listdir(path_to_wiki_pages)
	num_pages = len(wiki_dir)
	wiki_pages = []
	for page_index in range(0, num_pages):
		page_name = wiki_dir[page_index]
		print (page_name[:-5])
		with open(path_to_wiki_pages + page_name, 'r') as page:
			wiki_pages.append(Wiki_Page(page_name, get_keyword_frequency(page.read())))
			print('\t%s' % wiki_pages[page_index])


'''

