# ==== code ESP32 ====

import _thread
import time
from machine import UART, Pin, Timer
#import neopixel
from neopixel import NeoPixel
from random import randint
import math


# intensity asymptotique:
equilibre=2

# alpha = exp(-Te/tau)
alpha = 0.97

# backing array for led intensity:
# (this array is filled by UART received data)
backing = [equilibre for i in range(142)]


# init uart: rxbuf=256 ? 1024 ?
uart = UART(1, baudrate=115200, tx=19, rx=18)
#uart.write('hello')  # write 5 bytes
#uart.read(5)         # read up to 5 bytes

# init neopixel avec 142 leds
# la numerotation commence avec la premiere led en bas a gauche (colonne a 8 leds)
# et la derniere en haut a droite
# attention, ca fait des zigzag !
# et les colonnes alternent entre 8 et 9 leds
np = NeoPixel(Pin(0, Pin.OUT), 142)  # set GPIO0 to output to drive NeoPixels
for i in range(142):
    v=round(backing[i])
    np[i] = (v,v,v)
    #np[i] = (equilibre, equilibre, equilibre)
np.write()

#def write():
#    while True:
#        uart.write('hello')
#        time.sleep(0.5)

#_thread.start_new_thread(write, ())


def scintillation():
    #print("scintillation")
    for i in range(142):
        backing[i] = equilibre + (backing[i]-equilibre) * alpha
        #r = randint(0,1)
        #r=0
        if backing[i]<1.9:
            v=0
        else:
            v=math.floor(backing[i])
        np[i] = (v,v,v)
        #np[i] = equilibre + (np[i]-equilibre) * alpha
    np.write()


def receive_uart():
    while is_running_uart:
        if uart.any() > 0:
            print(str(uart.any())+ " bytes from uart...")
            data = uart.read()
            for i in range(len(data)):
                backing[i] = data[i]
                #np[i] = (data[i],data[i],data[i])
        pass

is_running_uart=True
_thread.start_new_thread(receive_uart, ())

tim = Timer(0)
tim.init(period=250, mode=Timer.PERIODIC, callback=lambda t:scintillation())
