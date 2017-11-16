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

FoodDrop.ping()
FoodDrop.blink()
FoodDrop.setup()
#FoodDrop.sendCategories()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup() #Clean up GPIO on CTRL+C exit
