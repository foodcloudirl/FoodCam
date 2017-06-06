import RPi.GPIO as GPIO
import time
import os
import pycurl
from StringIO import StringIO
from urllib import urlencode
import json
import threading
import FoodCam

print('************* FOODCAM v1.2 *****************');

FoodCam.ping()
FoodCam.blink()

try:
    while True:
        time.sleep(10)
except KeyboardInterrupt:
    GPIO.cleanup() #Clean up GPIO on CTRL+C exit
    GPIO.cleanup() #Clean up GPIO on normal exit