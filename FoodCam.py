import RPi.GPIO as GPIO
import time
import os
import pycurl
from StringIO import StringIO
from urllib import urlencode
import json
import threading
import settings
import socket

#GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(settings.button, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(settings.blue, GPIO.OUT) #blue
GPIO.setup(settings.red, GPIO.OUT) #red
GPIO.setup(settings.amber, GPIO.OUT) #amber
GPIO.setup(settings.green, GPIO.OUT) #green
GPIO.output(settings.blue, settings.off) #blue led off
GPIO.output(settings.red, settings.off) #red led off
GPIO.output(settings.amber, settings.off) #amber led off
GPIO.output(settings.green, settings.off) #green led off

buffer = StringIO()
image_control = pycurl.Curl()
image_control.setopt(image_control.URL,'localhost:8080/0/action/snapshot')
slack = pycurl.Curl()
#slack.setopt(slack.URL,settings.slackUrl)
slack.setopt(slack.URL,settings.slackUrl)#foodcam-test channel url
slack.setopt(slack.HTTPHEADER,['Accept: application/json'])
slack.setopt(slack.POST,1)
slackTest = pycurl.Curl()
slackTest.setopt(slack.URL,settings.slackTestUrl)
slackTest.setopt(slack.HTTPHEADER,['Accept: application/json'])
slackTest.setopt(slack.POST,1)
slackTest.setopt(slackTest.WRITEDATA,buffer)

network_warning = False

def ping():
    threading.Timer(60.0, ping).start()#300
    timer = time.gmtime()
    ip = get_ip_address()
    slackTest.setopt(slackTest.POSTFIELDS,'{"text":"ping from '+settings.location+' foodcam ('+ip+'): '+time.strftime('%b %d %Y %H:%M:%S',timer)+'"}')
    slackTest.perform()
    network_warning = (slackTest.getinfo(pycurl.RESPONSE_CODE) != 200)
    if network_warning:
        print("Network issue: "+str(slackTest.getinfo(pycurl.RESPONSE_CODE)))
    print("button ping: "+ip+", "+time.strftime('%b %d %Y %H:%M:%S',timer)+" UTC")

def blink():
    GPIO.output(settings.blue, settings.on) #blue led on
    if network_warning:
        GPIO.output(settings.red, settings.on) #red led on
    time.sleep(1)
    GPIO.output(settings.blue, settings.off) #blue led off
    if network_warning:
        GPIO.output(settings.red, settings.off) #red led off
    threading.Timer(1.0, blink).start()

def get_ip_address():
    ip_address = '';
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8",80))
    ip_address = s.getsockname()[0]
    s.close()
    return ip_address

def capture(channel):
    if network_warning:
        GPIO.output(settings.red, settings.on) #red led on
        time.sleep(0.1)
        GPIO.output(settings.red, settings.off) #red led off
        time.sleep(0.1)
        GPIO.output(settings.red, settings.on) #red led on
        time.sleep(0.1)
        GPIO.output(settings.red, settings.off) #red led off
        time.sleep(0.1)
        GPIO.output(settings.red, settings.on) #red led on
        time.sleep(0.1)
        GPIO.output(settings.red, settings.off) #red led off
        time.sleep(0.1)
        GPIO.output(settings.red, settings.on) #red led on
        time.sleep(0.1)
        GPIO.output(settings.red, settings.off) #red led off
        time.sleep(0.1)
    else:
        GPIO.output(settings.red, settings.on) #red led on
        print('Button Pressed, channel '+str(channel))
        time.sleep(1)
        image_control.perform()
        time.sleep(0.6)
        GPIO.output(settings.red, settings.off) #red led off
        GPIO.output(settings.amber, settings.on) #amber led on
        os.system('bash /home/pi/FoodCam/dropbox_uploader.sh upload /home/pi/motion/lastsnap.jpg /')
        time.sleep(1)
        filename = os.readlink('/home/pi/motion/lastsnap.jpg')
        print(filename)
        bashIO = os.popen('bash /home/pi/FoodCam/dropbox_uploader.sh share /'+filename).read()
        print(bashIO)
        url = bashIO.split('link: ')[1].replace('dl=0\n','raw=1')
        print("dropbox url: "+str(url))
        data = {'attachments':[{
            'fallback':'A picture of tasty surplus food!',
            'text':'Hello '+settings.recipient+', there is surplus food available in '+settings.location+'!',
            'image_url':str(url)
        }]}
        print(data)
        js = json.dumps(data)
        slack.setopt(slack.POSTFIELDS,js)
        slack.perform()
        GPIO.output(settings.amber, settings.off) #amber led off
        GPIO.output(settings.green, settings.on) #green led on
        print('sent to slack')
        time.sleep(3)
        GPIO.output(settings.green, settings.off) #green led off

GPIO.add_event_detect(settings.button, GPIO.FALLING, callback=capture, bouncetime=20000)

def exit():
    GPIO.cleanup() #Clean up GPIO on CTRL+C exit

