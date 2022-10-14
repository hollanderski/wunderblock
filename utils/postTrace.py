import requests

audiofile="sound.mp3"
bumpmapfile="bumpmap.png"
mapfile="map.png"

# Send POST request
files = {
	"audio" : open(audiofile, 'rb'),
	"bumpmap" : open(bumpmapfile, 'rb'),
	"map" : open(mapfile, 'rb'),
}

response = requests.post('http://wunderblock.ninonlm.com/traces', files=files)

print(response.content)

import uuid

unique_filename = str(uuid.uuid4())