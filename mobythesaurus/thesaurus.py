path_to_thesaurus = './'
clusters = []
with open( path_to_thesaurus + 'mobythes.aur') as file:
	for line in file:
		groups = line.split('\r')
		for group in groups: 
			clusters.append(group.split(','))	

print clusters