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
GPIO.setup(settings.bakery, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(settings.grocery, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(settings.pantry, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(settings.chilled, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(settings.non_food, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(settings.blue, GPIO.OUT) #blue
GPIO.setup(settings.red, GPIO.OUT) #red
GPIO.setup(settings.amber, GPIO.OUT) #amber
GPIO.setup(settings.green, GPIO.OUT) #green
GPIO.setup(settings.bakery_led, GPIO.OUT)
GPIO.setup(settings.grocery_led, GPIO.OUT)
GPIO.setup(settings.pantry_led, GPIO.OUT)
GPIO.setup(settings.chilled_led, GPIO.OUT)
GPIO.setup(settings.non_food_led, GPIO.OUT)

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

network_warning = False
has_bakery=0
has_grocery=0
has_pantry=0
has_chilled=0
has_non_food=0


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
    GPIO.output(settings.blue, settings.on) #blue led on
    if network_warning:
        GPIO.output(settings.red, settings.on) #red led on
    time.sleep(1)
    GPIO.output(settings.blue, settings.off) #blue led off
    if network_warning:
        GPIO.output(settings.blue, settings.off) #red led off
    threading.Timer(1.0, blink).start()

def get_ip_address():
    ip_address = '';
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8",80))
    ip_address = s.getsockname()[0]
    s.close()
    return ip_address

def resetCategories():
    global has_bakery=0
    global has_grocery=0
    global has_pantry=0
    global has_chilled=0
    global has_non_food=0
resetCategories()

def authCopia():
    #curl -c cookie.jar -i --data "email=some.email@address.com&password=somepassword"  https://copia-c.food.cloud
    print("todo")
authCopia()

def updateCategoryLights():
    if has_bakery==1:
        GPIO.output(settings.bakery_led, settings.on)
    else:
        GPIO.output(settings.bakery_led, settings.off)
    if has_grocery==1:
        GPIO.output(settings.grocery_led, settings.on)
    else:
        GPIO.output(settings.grocery_led, settings.off)
    if has_pantry==1:
        GPIO.output(settings.pantry_led, settings.on)
    else:
        GPIO.output(settings.pantry_led, settings.off)
    if has_chilled==1:
        GPIO.output(settings.chilled_led, settings.on)
    else:
        GPIO.output(settings.chilled_led, settings.off)
    if has_non_food==1:
        GPIO.output(settings.non_food_led, settings.on)
    else:
        GPIO.output(settings.non_food_led, settings.off)
    print("Categories: "+str(has_bakery)+","+str(has_grocery)+","+str(has_pantry)+","+str(has_chilled)+","+str(has_non_food)+".")

def sendCategories(channel):
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
    print("Sent")
    resetCategories()

def addCategory(channel):
    print("Button pressed on channel: "+str(channel))
    if channel==settings.bakery:
        has_bakery = 1
        print("bakery")
    elif channel==settings.grocery:
        has_grocery = 1
        print("grocery")
    elif channel==settings.pantry:
        has_pantry = 1
        print("pantry")
    elif channel==settings.chilled:
        has_chilled = 1
        print("chilled")
    elif channel==settings.non_food:
        has_non_food = 1
        print("non_food")
    else:
        print("Unknown category")
    updateCategoryLights()

resetCategories()
def setup():
    GPIO.add_event_detect(settings.bakery, GPIO.FALLING, callback=addCategory, bouncetime=2000)
    GPIO.add_event_detect(settings.grocery, GPIO.FALLING, callback=addCategory, bouncetime=2000)
    GPIO.add_event_detect(settings.pantry, GPIO.FALLING, callback=addCategory, bouncetime=2000)
    GPIO.add_event_detect(settings.chilled, GPIO.FALLING, callback=addCategory, bouncetime=2000)
    GPIO.add_event_detect(settings.non_food, GPIO.FALLING, callback=addCategory, bouncetime=2000)
    GPIO.add_event_detect(settings.button, GPIO.FALLING, callback=sendCategories, bouncetime=2000)

def exit():
    GPIO.cleanup() #Clean up GPIO on CTRL+C exit

