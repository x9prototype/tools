#!/usr/bin/env python
#
# download_album.py is a simple script where you can supply the flickr album ID
# and it will download all of the album's images. It will rename the images to
# the original file name, instead of <hash>.jpg that flickr uploads them to.
# 
# Note 1:
# This was a quick hack, and may overwrite/delete files. Use at your own risk.
#
# Note 2:
# Don't forget to put your flickr API key & secret in the correct areas of the
# script. You can get a flickr API key here: flickr.com/services/api/keys/apply
#
# Usage:
# ./download_album.py <album_id>
#
# Example:
# https://secure.flickr.com/photos/swedish_heritage_board/sets/72157626187237232/
# ./download_album.py 72157626187237232
#

import flickrapi
import urllib
import urlparse, os, sys
import string

api_key = 'stick_your_api_key_here'
api_secret = 'stick_your_api_secret_here'

# Check to see if a file exists, and if so, return the name with a modifier
# at the end, if not, return filename
def fileIncrementName(directory, filename):
    basename = os.path.basename(filename)
    head, tail = os.path.splitext(basename)
    dst_file = os.path.join(directory, basename)
    # rename if necessary
    count = 0
    while os.path.exists(dst_file):
        count += 1
        dst_file = os.path.join(directory, '%s-%d%s' % (head, count, tail))
    #print 'Renaming %s to %s' % (filename, dst_file)
    return dst_file

# Makes a string safe for filenames
def sanitizeFilename(filename):
	valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
	return ''.join(c for c in filename if c in valid_chars)

if(len(sys.argv) < 2):
	print "Error: Please supply a Photoset ID from Flickr to download!"
	quit()

baseFolder = 'photos'
if not os.path.exists(baseFolder):
	os.makedirs(baseFolder)

photosetID = sys.argv[1]

flickr = flickrapi.FlickrAPI(api_key, api_secret)

(token, frob) = flickr.get_token_part_one(perms='read')
if not token: raw_input("Press ENTER after you authorized this program")
flickr.get_token_part_two((token, frob))

set = flickr.photosets_getInfo(photoset_id=photosetID)
setTitle = set.findall('photoset')[0].findall('title')[0].text

# Create a directory with the title of the album
titleFolder = "%s\%s" % (baseFolder, setTitle)
if not os.path.exists(titleFolder):
	os.makedirs(titleFolder)

# Walk the album and extract the photo urls
for photo in flickr.walk_set(photosetID):
	photoName = sanitizeFilename(photo.get('title'))
	print "Downloading photo data for %s" % photoName
	photoSizes = flickr.photos_getSizes(photo_id=photo.get('id'))
	for photoURL in photoSizes.find('sizes').findall('size'):
		if photoURL.get('label') == "Original":
			photoSource = photoURL.get('source')
			# Figure out photo extension
			path = urlparse.urlparse(photoSource).path
			ext = os.path.splitext(path)[1]
			# Create the filename
			photoFilename = "%s%s" % (photoName, ext)
			# Do the download
			photoFile = urllib.URLopener()
			photoFile.retrieve(photoSource, fileIncrementName(titleFolder, photoFilename))
