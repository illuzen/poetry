from bs4 import BeautifulSoup
import re
import requests
import os

kMAX_LINKS = 20

def get_links(link):
    linkNum = 1
    if not re.match(r'http://|https://',link):
            link = "http://"+link

#    f.write(str(linkNum)+', '+link+'\n')
    linkDir = re.split('/wiki/',link)[1]
    if not os.path.exists(linkDir):
        os.makedirs(linkDir)

    linkSet = set([link])
    print linkSet

    r  = requests.get(link)
    data = r.text.encode('utf-8')
    soup = BeautifulSoup(data)

    exclude = 'wikidata.org|#|:|%|Terms_of_Use|wikimediafoundation.org|.wikipedia.org|Main_Page'
    include = '/wiki/'
    for link in soup.find_all('a'):
        if link.get('href') and re.search('/wiki/',link.get('href')) and not re.search(exclude,link.get('href')):
                link = 'http://wikipedia.org'+link.get('href')
                if(link not in linkSet):
                    r  = requests.get(link)
                    linkData = r.text.encode('utf-8')
                    linkNum=linkNum+1
                    print 'linkNum = '+str(linkNum)
                    print(link)
                    linkSubject = re.split('/wiki/',link)[1]
                    linkPath=os.getcwd()+'/'+linkDir+'/'+linkSubject
                    linkHtml = open(linkPath,'w')
                    linkHtml.write(linkData)
                    linkHtml.close()
#                    f.write(str(linkNum)+', '+link+'\n')
                    linkSet.update([link])
                    if linkNum >= kMAX_LINKS:
                        break

#    f.close()
    #print(linkSet)


if __name__ == '__main__':
    #f = open('linkFile.csv', 'w')
    link = raw_input("Enter a wikipedia page to extract links from:")
    get_links(link)

