import requests, json
import sqlite3
import hashlib
from queue import Queue
from threading import Thread
import time
import random
import sys

DB_TABLE = "imageHashes"
TABLE_LAYOUT = "(num INTEGER PRIMARY KEY, ext TEXT, checksum TEXT)"
IMAGE_URL = "https://static.f-list.net/images/charimage/{}.{}"
DATABASE_URL = "https://nyc3.digitaloceanspaces.com/fari/hashes.db"

def get_image(url, forms = {}):
		succeeded = False
		while not succeeded:
			try:
				headers = {'user-agent' : 'Python/3.7.0 (Lookout) I\m generating checksums of these images!'}
				resp = requests.get(url)
				succeeded = True
			except Exception as e:
				print(e)
				time.sleep(1+random.random())
		if resp != None and resp.status_code == 200:
			return resp
		
		return None
		
def get_db(url, forms = {}):
		succeeded = False
		while not succeeded:
			try:
				headers = {'user-agent' : 'Python/3.7.0 (Lookout) DB download'}
				resp = requests.get(url)
				succeeded = True
			except Exception as e:
				print(e)
				time.sleep(10)
		if resp != None and resp.status_code == 200:
			return resp
		
		return None
	
def post_json(url, forms = {}):
	succeeded = False
	while not succeeded:
		try:
			headers = {'user-agent' : 'Python/3.7.0 (Windows 10 NT) Lookout'}
			resp = requests.post(url, data=forms, timeout=10)
			succeeded = True
		except Exception as e:
			print(e)
	return resp.json()
	
def request_ticket(account, pw):
	forms = {"account" : account, "password" : pw, "no_characters" : "true"}
	ticket_json = post_json('https://www.f-list.net/json/getApiTicket.php', forms)
	if ticket_json['error'] == '':
		return ticket_json['ticket']
	else:
		return None
		
def request_character(account, name, ticket):
	forms = {"account" : account, "ticket" : ticket, "name" : name}
	character_json = post_json('https://www.f-list.net/json/api/character-data.php', forms)
	return character_json
	
def connect_and_setup_db():
	try:
		db = sqlite3.connect('hashes.db')
		result = db.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='{}'".format(DB_TABLE))
		if result.fetchall()[0][0] == 0:
			raise SQLiteException()
		return db
	except:
		print("Downloading hash database from remote server...")
		db_file = get_db(DATABASE_URL)
		if db_file != None:
			print("Saving hash database locally (for future use).")
			with open('hashes.db', 'wb') as f:
				for block in db_file.iter_content(1024):
					f.write(block)
			print("Done!")
			return connect_and_setup_db()
		else:
			print("Failed to download the database!")
			return None
	
def print_all_matches(img_nums, matches):
	if len(matches) <= 0:
		print("No profiles using the same images as the one provided were found.")
		return
	print("Found the following images that match images on the provided profile:")
	for match in matches:
		print(IMAGE_URL.format(match[0],match[1]))
	
def find_hash_matches(img_list, db):
	img_nums = [int(i["image_id"]) for i in img_list]
	filtered_matches = []
	for img in img_list:
		sys.stdout.write("\rChecking image {} of {}...".format(img_list.index(img)+1, len(img_list)))
		sys.stdout.flush()
		img_meta = (img["image_id"], img["extension"])
		img = get_image(IMAGE_URL.format(img_meta[0], img_meta[1]))
		if img != None:
			hash = hashlib.md5(img.content).hexdigest()
			matches = db.execute("SELECT num,ext FROM {} WHERE checksum = ?".format(DB_TABLE), (hash,))
			filtered_matches = filtered_matches + [x for x in matches.fetchall() if not x[0] in img_nums]
	print()
	print_all_matches(img_nums, filtered_matches)
	
def update_db():
	db = connect_and_setup_db()
	if db != None:
		username = input("Enter your account username: ")
		pw = input("Enter your account password: ")
		ticket = request_ticket(username, pw)
		if ticket != None:
			name = input("Enter the name of the character you wish to check: ")
			form = {"name" : name}
			char_json = request_character(username, name, ticket)
			find_hash_matches(char_json["images"], db)
		else:
			print("Could not get a ticket with the login you provided. Try again.")

if __name__ == "__main__":
	update_db()