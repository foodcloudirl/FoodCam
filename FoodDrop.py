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

copia = pycurl.Curl()
copia.setopt(copia.URL,settings.copiaUrl)#foodcam-test channel url
copia.setopt(copia.HTTPHEADER,['Accept: application/json'])
copia.setopt(copia.POST,1)


GPIO.output(23, settings.off) #green led off

network_warning = False


def ping():
    threading.Timer(60.0, ping).start()#300
    timer = time.gmtime()
    ip = get_ip_address()
    slackTest.setopt(slackTest.POSTFIELDS,'{"text":"ping from '+settings.location+' fooddrop ('+ip+'): '+time.strftime('%b %d %Y %H:%M:%S',timer)+'"}')
    slackTest.perform()
    network_warning = (slackTest.getinfo(pycurl.RESPONSE_CODE) != 200)
    if network_warning:
        print("Network issue: "+str(slackTest.getinfo(pycurl.RESPONSE_CODE)))
    print("button ping: "+ip+", "+time.strftime('%b %d %Y %H:%M:%S',timer)+" UTC")

def blink():
    GPIO.output(17, settings.on) #blue led on
    if network_warning:
        GPIO.output(18, settings.on) #red led on
    time.sleep(1)
    GPIO.output(17, settings.off) #blue led off
    if network_warning:
        GPIO.output(18, settings.off) #red led off
    threading.Timer(1.0, blink).start()

def get_ip_address():
    ip_address = '';
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8",80))
    ip_address = s.getsockname()[0]
    s.close()
    return ip_address

def resetCategories():
    has_bakery=0
    has_grocery=0
    has_pantry=1
    has_chilled=0
    has_non_food=0

def authCopia():
    #curl -c cookie.jar -i --data "email=some.email@address.com&password=somepassword"  https://copia-c.food.cloud
    print("todo")

def updateCategoryLights():
    if has_bakery:
        GPIO.output(settings.bakery, settings.on)
    else:
        GPIO.output(settings.bakery, settings.off)
    if has_grocery:
        GPIO.output(settings.grocery, settings.on)
    else:
        GPIO.output(settings.grocery, settings.off)
    if has_pantry:
        GPIO.output(settings.pantry, settings.on)
    else:
        GPIO.output(settings.pantry, settings.off)
    if has_chilled:
        GPIO.output(settings.chilled, settings.on)
    else:
        GPIO.output(settings.chilled, settings.off)
    if has_non_food:
        GPIO.output(settings.non_food, settings.on)
    else:
        GPIO.output(settings.non_food, settings.off)

def sendCategories():
    cat_text = ""
    if has_bakery:
        cat_text+="bakery, "
    if has_grocery:
        cat_text+="grocery, "
    if has_pantry:
        cat_text+="pantry, "
    if has_chilled:
        cat_text+="chilled, "
    if has_non_food:
        cat_text+="non_food, "
    data = {
        'text':'Hello '+settings.recipient+', there is '+cat_text[:-2]+' available in '+settings.location+'!'
    }
    print(data)
    js = json.dumps(data)
    slack.setopt(slack.POSTFIELDS,js)
    slack.perform()

def addCategory(channel):
    if channel=settings.bakery:
        has_bakery = 1
    elif channel=settings.grocery:
        has_grocery = 1
    elif channel=settings.pantry:
        has_pantry = 1
    elif channel=settings.chilled:
        has_chilled = 1
    elif channel=settings.non_food:
        has_non_food = 1
    else print("Unknown category")
    updateCategoryLights()
    print("Categories: "+has_bakery+","+has_grocery+","+has_pantry+","+has_chilled+","+has_non_food+".")

resetCategories()
GPIO.add_event_detect(settings.bakery, GPIO.FALLING, callback=addCategory, bouncetime=2000)
GPIO.add_event_detect(settings.grocery, GPIO.FALLING, callback=addCategory, bouncetime=2000)
GPIO.add_event_detect(settings.pantry, GPIO.FALLING, callback=addCategory, bouncetime=2000)
GPIO.add_event_detect(settings.chilled, GPIO.FALLING, callback=addCategory, bouncetime=2000)
GPIO.add_event_detect(settings.non_food, GPIO.FALLING, callback=addCategory, bouncetime=2000)

GPIO.add_event_detect(settings.button, GPIO.FALLING, callback=sendCategories, bouncetime=2000)

def exit():
    GPIO.cleanup() #Clean up GPIO on CTRL+C exit

