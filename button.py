import RPi.GPIO as GPIO
import time
import os
import pycurl
from StringIO import StringIO
from urllib import urlencode
import json
import threading
import settings

#GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(17, GPIO.OUT) #blue
GPIO.setup(18, GPIO.OUT) #red
GPIO.setup(22, GPIO.OUT) #amber
GPIO.setup(23, GPIO.OUT) #green

GPIO.output(17, GPIO.HIGH) #blue led on
print('hello');

buffer = StringIO()
dropbox = pycurl.Curl()
dropbox.setopt(dropbox.URL,'localhost:8080/0/action/snapshot')
#dropbox.setopt(c.WRITEDATA,buffer)
slack = pycurl.Curl()
#slack.setopt(slack.URL,settings.slackUrl)
slack.setopt(slack.URL,settings.slackTestUrl)#foodcam-test channel url
slack.setopt(slack.HTTPHEADER,['Accept: application/json'])
slack.setopt(slack.POST,1)
slackTest = pycurl.Curl()
slackTest.setopt(slack.URL,settings.slackTestUrl)
slackTest.setopt(slack.HTTPHEADER,['Accept: application/json'])
slackTest.setopt(slack.POST,1)

def ping():
    threading.Timer(300.0, ping).start()
    timer = time.gmtime()
    print "button ping: "+time.strftime('%b %d %Y %H:%M:%S',timer)
    slackTest.setopt(slackTest.POSTFIELDS,'{"text":"ping foodcam v1: '+time.strftime('%b %d %Y %H:%M:%S',timer)+'"}')
    slackTest.perform()

def blink():
    GPIO.output(17, GPIO.LOW) #blue led off
    time.sleep(1)
    GPIO.output(17, GPIO.HIGH) #blue led on
    threading.Timer(1.0, blink).start()

ping()
blink()


while True:
    input_state = GPIO.input(4)    
    if input_state == True:
        time.sleep(0.1)
    else:
        GPIO.output(18, GPIO.HIGH) #red led on
        print('Button Pressed')
        dropbox.perform()
        time.sleep(1)
        GPIO.output(18, GPIO.LOW) #red led off
        GPIO.output(22, GPIO.HIGH) #amber led on
        os.system('bash /home/pi/button/dropbox_uploader.sh upload /home/pi/motion/lastsnap.jpg /')
        time.sleep(1)
        filename = os.readlink('/home/pi/motion/lastsnap.jpg')
        print(filename)
        bashIO = os.popen('bash /home/pi/button/dropbox_uploader.sh share /'+filename).read()
        print(bashIO)
        url = bashIO.split('link: ')[1].replace('dl=0\n','raw=1')
        print("dropbox url: "+str(url))
        data = {'attachments':[{
            'fallback':'Should be an image of tasty surplus food',
            'text':'Hello, there is food going in the kitchen!!',
            'image_url':str(url)
        }]}
        print(data)
        js = json.dumps(data)
        slack.setopt(slack.POSTFIELDS,js)
        slack.perform()
        GPIO.output(22, GPIO.LOW) #amber led off
        GPIO.output(23, GPIO.HIGH) #green led on
        print('sent to slack')
        time.sleep(2)
        GPIO.output(23, GPIO.LOW) #green led off
