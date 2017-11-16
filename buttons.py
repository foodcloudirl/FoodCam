import RPi.GPIO as GPIO
import time
import os
import pycurl
from StringIO import StringIO
from urllib import urlencode
import json
import threading
import FoodDrop

print('************* FOODDROP v1.0 *****************');

FoodCam.ping()
FoodCam.blink()

try:
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    GPIO.cleanup() #Clean up GPIO on CTRL+C exit
