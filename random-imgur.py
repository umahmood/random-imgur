#!/usr/bin/env python3 
import os
import sys
import random
import hashlib
import argparse

import requests
import requests.exceptions

def get_imgur_url():
	"""
	Builds an imgur url in the form http://i.imgur.com/{5 characters}.jpg. 

	@return: (tuple) - url (string), file name (string) 
	"""
	imgur_url = "http://i.imgur.com/"
	ext = ".jpg"
	r1 = random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
	r2 = random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
	r3 = random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
	r4 = random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
	r5 = random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')

	code = r1 + r2 + r3 + r4 + r5 
	file_name = code
	full_url = imgur_url + file_name + ext

	return (full_url, file_name)

def is_placeholder_image(img_data):
	"""
	Checks for the placeholder image. If an imgur url is not valid (such as 
	http//i.imgur.com/12345.jpg), imgur returns a blank placeholder image. 

	@param: img_data (bytes) - bytes representing the image.

	@return: (boolean) True if placeholder image otherwise False
	"""
	sha256_placeholder = "9b5936f4006146e4e1e9025b474c02863c0b5614132ad40db4b925a10e8bfbb9"
	m = hashlib.sha256()
	m.update(img_data)
	return 	m.hexdigest() == sha256_placeholder

def save_image(download_dir, file_name, file_ext, img_data):
	"""
	Saves an image to the download directory with a given file name and extension.

	@param: img_data     (bytes) - bytes representing the image.
	@param: file_name    (string) - name to the save the file as i.e. foo.jpg.
	@param: download_dir (string) - path to the download directory.

	@return: None
	"""
	try:
		file_path = "{0}{1}{2}.{3}".format(download_dir, os.sep, file_name, file_ext)
		with open(file_path, "wb") as f:
			f.write(img_data)
	except FileNotFoundError as e:
		raise e

def download_imgur(url):
	"""
	Downloads an image from imgur.

	@param: url (string) - Imgur url to download i.e. http://i.imgur.com/1a2b3c.jpg.

	@return: None if the download fails else images binary data and content type.
	"""
	try:
		r = requests.get(url)
		if not r.ok:
			return None
		sub_type = r.headers["content-type"][6:] # turns image/gif to gif
		file_type = "jpg" if sub_type not in ["gif", "webm", "png"] else sub_type
		return r.content, file_type
	except (exceptions.ConnectionError, exceptions.HTTPError) as e:
		pass

def main(max_imgs, download_dir):
	count = 0
	while count < max_imgs:
		imgur_url, file_name = get_imgur_url()
		img_data, file_type = download_imgur(imgur_url)
		if not img_data or is_placeholder_image(img_data):
			continue
		save_image(download_dir, file_name, file_type, img_data)
		count += 1

if __name__ == '__main__':
	parser = argparse.ArgumentParser(description="Process command line arguments for " + __file__)
	parser.add_argument('--img', type=int, required=True, nargs='?', help='number of images to download.')
	parser.add_argument('--dir', type=str, default="downloaded_imgurs", nargs='?', help="download directory.")
	
	args = parser.parse_args()

	if not os.path.exists(args.dir): 
		os.mkdir(args.dir)

	sys.exit(main(args.img, args.dir))
