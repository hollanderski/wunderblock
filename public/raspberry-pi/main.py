import _thread
import time
import numpy as np
from gpiozero import MCP3001, LED
# pour le traitement d'image post acquisition :
import requests
import cv2
import os
import serial

np.set_printoptions(linewidth=200, threshold=1500)

#adc=MCP3001()

# la numerotation des pins suit le schema BCM (gpio readall)
# les entrees EN des mux analo sont active LOW (donc elles doivent
# etre initialement HIGH

# mux "B" (lents, CI traversants, en haut) : write 3.3V
outEN0=LED(6, initial_value=True)
outEN1=LED(13, initial_value=True)

out0=LED(4)
out1=LED(17)
out2=LED(27)
out3=LED(22)

# selectionne le mux_B de gauche
def selectCols0to15():
	outEN1.value=1
	outEN0.value=0

# et celui de droite
def selectCols16to31():
	outEN1.value=0
	outEN0.value=1

# mux "A" (rapides, sparkfun, sur le cote) : read (ADC)
inEN0=LED(19, initial_value=True)
inEN1=LED(26, initial_value=True)

in0=LED(18)
in1=LED(23)
in2=LED(24)
in3=LED(25)

# selectionne le mux inferieur (lignes 0 a 15)
def selectLines0to15():
	inEN1.value=1
	inEN0.value=0

# et celui d'en haut (lignes 16 a 31)
def selectLines16to31():
	inEN1.value=0
	inEN0.value=1

print("GPIO init ok")

adc=MCP3001()
print("ADC init ok")

trace=np.zeros((32,32), dtype=int)
traceCalib=np.zeros((32,32), dtype=int)

# convertit entre 0 et 100 la valeur lue sur l'ADC
# relié à une ligne donnée. Applique un seuillage.
def readADC():
	v =  round(200*adc.value)
	if v > 99:
		v = 0
	#elif v < 10:
	#	v = 0
	time.sleep(0.001)
	return v

def seuil(v):
	if v < 0:
		return 0
	return v

# utile pour selectColumn(i):
# table qui a chaque numero des bandes de cuivre
# associe la bonne sorties du MUXB_0 (ou 1, meme cablage tordu)
# de telle sorte que selectColumnMuxOutput(remapColumnsToCopper[c])
# active la bande de cuivre correcte:
remapColumnsToCopper=(8,9,10,11,12,13,14,15,7,6,5,4,3,2,1,0)

# a l'interieur d'un bloc de 16 colonnes,
# connecte la sortie "i" du MUX B au 3V3
# (muxs lents situes sur le cote superieur du PCB)
def selectColumnMuxOutput(i):
	out0.value=(i & 1)
	out1.value=(i & 2) >> 1
	out2.value=(i & 4) >> 2
	out3.value=(i & 8) >> 3

# connecte l'entree "i" du MUX A a l'entree de l'ADC
# (muxs rapide situes sur le cote gauche du PCB)
def selectLineMuxInput(i):
	in0.value=(i & 1)
	in1.value=(i & 2) >> 1
	in2.value=(i & 4) >> 2
	in3.value=(i & 8) >> 3

# mux_A dits "IN" (rapides, sur le cote)
# faire inEN0=0 puis inEN1=0 alternativement
def readLines(col):
	selectLines0to15()
	for line in range(16):
		selectLineMuxInput(line)
		#print(line, 100*adc.value)
		trace[line, col]=seuil(readADC()-traceCalib[line, col])
	selectLines16to31()
	for line in range(16):
		selectLineMuxInput(line)
		#print(line, 100*adc.value)
		trace[line+16, col]=seuil(readADC()-traceCalib[line+16, col])


# active une colonne apres l'autre en la connectant au 3V3
# pendant que les autres sont deconnectees
def sweepColumns():
	selectCols0to15()
	for col in range(16):
		selectColumnMuxOutput(remapColumnsToCopper[col])
		readLines(col)
	selectCols16to31()
	for col in range(16):
		selectColumnMuxOutput(remapColumnsToCopper[col])
		readLines(col+16)


def calib():
	global traceCalib
	traceCalib=np.zeros((32,32), dtype=int)
	sweepColumns()
	traceCalib = np.array(trace, dtype=int)

def scan():
	sweepColumns()
	print("---------------------------------------------")
	print(trace)

def scanContinuous():
	while is_running_scan_thread==True:
		sweepColumns()
		print("---------------------------------------------")
		print(trace)
		print(trace.min(), " -> ", trace.max())
		#scipy.io.savemat("hand.mat", {'data':trace})
		time.sleep(0.2)

def startScanThread():
    global is_running_scan_thread
    is_running_scan_thread=True
    _thread.start_new_thread(scanContinuous, ())



# requete post:

#https://stackoverflow.com/questions/22567306/how-to-upload-file-with-python-requests
#https://stackoverflow.com/questions/22567306/how-to-upload-file-with-python-requests
#il fait d'abord des transformations d'images sur la trace et puis envoie la requête
#https://github.com/hollanderski/wunderblock/blob/main/utils/sendTrace.py
#les dépendences sont opencv et requests

def showImage():
	scan()
	img = np.zeros([32,32,1])
	img = img.astype("uint8")
	img[:,:,0] = trace
	#img[:,:,0] = (trace > (trace.max()-1)) * trace
	#cv2.imshow('image',img)
	#cv2.waitKey(0)
	#cv2.imwrite("trace"+str(round(time.time()))+".png", img)
	cv2.imwrite("trace.png", img)

# 1. Create the black & white texture (bumpmap) :
def sendPost():
	img = np.zeros([32,32,1])
	img = img.astype("uint8")
	img[:,:,0] = trace
	img = cv2.resize(img, (100, 100), interpolation = cv2.INTER_NEAREST)
	blur = cv2.GaussianBlur(img,(5,5),0)
	ret,thresh = cv2.threshold(blur,0, 255,  cv2.THRESH_BINARY+cv2.THRESH_OTSU)
	blur = cv2.GaussianBlur(thresh,(5,5),0)
	# TODO : generer un nom unique pour chaque image
	bumpmapfile = "bumpmap1"+".png"
	cv2.imwrite(bumpmapfile, blur)
	# 2. Create the rgb texture :
	# Skin texture masking
	skin = cv2.imread('texture.jpg')
	skin = cv2.resize(skin, (100, 100), interpolation = cv2.INTER_NEAREST)
	masked = cv2.bitwise_and(skin, skin, mask=cv2.bitwise_not(blur))
	alpha = np.sum(masked, axis=-1) > 0
	# Convert True/False to 0/255 and change type to "uint8" to match "na"
	alpha = np.uint8(alpha * 255)
	# Stack new alpha layer with existing image to go from BGR to BGRA, i.e. 3 channels to 4 channels
	res = np.dstack((masked, alpha))
	# TODO : generer un nom unique pour chaque image
	mapfile = "map1"+".png"
	cv2.imwrite(mapfile, res)
	# Send POST request
	#audiofile="sample1234.mp3"
	#bumpmapfile="bumpmap1234.png"
	#mapfile="map1234.png"
	#files = {
	#	"audio" : open(audiofile, 'rb'),
	#	"bumpmap" : open(bumpmapfile, 'rb'),
	#	"map" : open(mapfile, 'rb'),
	#	}
	#response = requests.post('http://wunderblock.ninonlm.com/traces', files=files)
	#print(response.content)

# son :
# os.system("arecord -d 5 -f S16_LE sample.mp3")
# unique file name : "map"+str(round(time.time()))+".png"

is_running_scan_thread=True
#scanContinuous()
while True:
	showImage()


#def main():
#    print("Hello World!")

#if __name__ == "__main__":
#    main()


# ==== uart send to ESP32 ===

ser = serial.Serial(
        port='/dev/ttyS0', #Replace ttyS0 with ttyAM0 for Pi1,Pi2,Pi0
        baudrate = 115200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        timeout=1
)

ser.write(bytes([10,10,10]))
