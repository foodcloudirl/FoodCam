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

FoodCam.capture(0)

FoodCam.exit()
