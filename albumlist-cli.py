import sqlite3
import argparse
from colorama import init, Fore

DATABASE = '/home/moritz/Music/Albenliste.db'

def labelPrint(str, type=''):
	if type == 'warning':
		print(Fore.YELLOW + '⚠ ' + str)
	elif type == 'success':
		print(Fore.GREEN + '✔ ' + str)
	elif type == 'error':
		print(Fore.RED + '❌ ' + str)
	else:
		print(str)

def printDatabase(orderBy = 'artist'):
	if orderBy not in {'artist', 'album', 'mediatype'}:
		labelPrint('Table only sortable by "artist", "album" or "mediatype"', 'warning')
		return
	con = sqlite3.connect(DATABASE)
	cur = con.cursor()
	i = 1
	for row in cur.execute('SELECT * FROM albums ORDER BY {} COLLATE NOCASE'.format(orderBy)):
		line = Fore.CYAN + str(i) + Fore.RESET
		print('{}: {} - {} ({})'.format(line, row[0], row[1], row[2]))
		i += 1
	con.close()
	
def addToDatabase(artist, album, mediatype):
	con = sqlite3.connect(DATABASE)
	cur = con.cursor()
	try:
		cur.execute("INSERT INTO albums(artist,album,mediatype) VALUES (?, ?, ?)", (artist, album, mediatype))
		con.commit()
		labelPrint('{} - {} ({}) added.'.format(artist, album, mediatype), 'success')
	except sqlite3.IntegrityError as e:
		if 'UNIQUE constraint failed' in str(e):
			labelPrint('{} - {} ({}) Already in Database.'.format(artist, album, mediatype), 'warning')
		else:
			labelPrint(e, 'error')
	finally:
		con.close()
		
def removeFromDatabase(artist, album, mediatype):
	con = sqlite3.connect(DATABASE)
	cur = con.cursor()
	try:
		cur.execute("DELETE FROM albums WHERE artist=(?) AND album=(?) AND mediatype=(?)", (artist, album, mediatype))
		con.commit()
		if con.total_changes > 0:
			labelPrint('{} - {} ({}) removed.'.format(artist, album, mediatype), 'success')
		else:
			labelPrint('{} - {} ({}) not found.'.format(artist, album, mediatype), 'warning')
	except sqlite3.IntegrityError as e:
		labelPrint(e, 'error')
	finally:
		con.close()
		
def searchInDatabase(artist, album, mediatype):
	con = sqlite3.connect(DATABASE)
	cur = con.cursor()
	try:
		cur.execute("SELECT * FROM albums WHERE artist=(?) AND album=(?) AND mediatype=(?)", (artist, album, mediatype))
		if len(cur.fetchall()) > 0:
			labelPrint('{} - {} ({}) present in database.'.format(artist, album, mediatype), 'success')
		else:
			labelPrint('{} - {} ({}) not found.'.format(artist, album, mediatype), 'warning')
	except sqlite3.IntegrityError as e:
		labelPrint(e, 'error')
	finally:
		con.close()
	
if __name__ == "__main__":
	# init colorama
	init(autoreset=True)
	
	# command line options
	parser = argparse.ArgumentParser()
	parser.add_argument('artist', help="Album artist. Use 'Various Artists' for VA releases")
	parser.add_argument('album', help="Album title.")
	parser.add_argument('mediatype', help="Album format. Either 'CD', 'Vin(yl)', 'Dig(ital)' or 'Cas(sette)'", type = str.lower)
	parser.add_argument("-v", "--verbose", help="Print the database afterwards", action="store_true")
	group = parser.add_mutually_exclusive_group()
	group.add_argument("-r", "--remove", help="Remove the album from the database", action="store_true")
	group.add_argument("-s", "--search", help="Check if the album is in the database", action="store_true")
	args = parser.parse_args()
	
	# shortcuts for mediatype
	if args.mediatype in {'cd', 'disk'}:
		args.mediatype = 'cd'
	if args.mediatype in {'vin'}:
		args.mediatype = 'vinyl'
	if args.mediatype in {'dig', 'digi'}:
		args.mediatype = 'digital'
	if args.mediatype in {'cas', 'cass', 'tape', 'mc'}:
		args.mediatype = 'cassette'
	
	# actual database modification
	if args.mediatype not in {'cd', 'vinyl', 'digital', 'cassette'}:
		labelPrint('"' + args.mediatype + '" is an unknown media type.', 'error')
		exit(0)
	
	if args.remove:
		removeFromDatabase(args.artist, args.album, args.mediatype)
	elif args.search:
		searchInDatabase(args.artist, args.album, args.mediatype)
	else:
		addToDatabase(args.artist, args.album, args.mediatype)
	if args.verbose:
		print()
		printDatabase()
	exit(0)
