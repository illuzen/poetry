import requests
import re


def get_artists_by_first_character(char):
	url = '%s%s.html' % (url_prefix, char)
	artists_html = requests.get(url).text
	for line in artists_html.split('\n'):
		match = re.match(artist_rx, line)
		if match:
			print 'artist', match.group(1)
			get_albums_by_artist(match.group(1))

def get_albums_by_artist(artist_link):
	url = '%s%s' % (url_prefix, artist_link)
	albums_html = requests.get(url).text
	line_idx = 0
	albums_html_lines = albums_html.split('\n')
	while line_idx < len(albums_html_lines):
		new_album_match = re.match(album_rx, albums_html_lines[line_idx])
		if new_album_match:
			print '\tnew album' #, new_album_match.group(1)
			line_idx += 1
			while len(albums_html_lines[line_idx]) > 1:
				song_match = re.match(song_rx, albums_html_lines[line_idx])
				print '\t\tsong', song_match.group(2)
				get_song_lyrics(song_match.group(1))
				line_idx += 1
#			get_songs_by_album(match.group(1))
		
		line_idx += 1

def get_song_lyrics(song_link):
	url = '%s%s' % (url_prefix, song_link)
	song_html = requests.get(url).text
	line_idx = 0
	song_html_lines = song_html.split('\n')
	while not re.match(lyrics_start_tag, song_html_lines[line_idx]):
		print song_html_lines[line_idx]
		line_idx += 1
	line_idx += 1

	while not re.match(lyrics_end_tag, song_html_lines[line_idx]):
		print song_html_lines[line_idx]
		line_idx += 1



# typical line <a href="i/immature.html">IMMATURE</a><br />

url_prefix = 'http://www.azlyrics.com/'
artist_rx = re.compile('<a href="([^"]*)">.*</a><br />')
album_rx  = re.compile('<div class="album">([^<]*)')#<"([^"]*)')
song_rx   = re.compile('<a href="([^>]*)" target="_blank">(.*)</a>')
lyrics_start_tag = '<!-- start of lyrics -->'
lyrics_end_tag = '<!-- end of lyrics -->'

for i in range(0, 26):
	char = chr(ord('a') + i)
	get_artists_by_first_character(char)
