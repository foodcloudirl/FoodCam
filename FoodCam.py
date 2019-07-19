import RPi.GPIO as GPIO
import time
from datetime import datetime
import os
import pycurl
from StringIO import StringIO
from urllib import urlencode
import json
import threading
import settings
import socket
import argparse
from picamera import PiCamera
import sys
sys.path.insert(0, '/home/pi/FoodCam/hx711py')
sys.path.insert(0, '/home/pi/FoodCam/rpi_ws281x/python')
from hx711 import HX711
from neopixel import *

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

camera = PiCamera()
camera.start_preview()

buffer = StringIO()
buffer2 = StringIO()
image_control = pycurl.Curl()
image_control.setopt(image_control.URL,'localhost:8080/0/action/snapshot')

server = pycurl.Curl()
server.setopt(server.URL,settings.foodcamServerUrl+"?api_token="+settings.foodcamServerKey)
server.setopt(server.HTTPHEADER,['Accept: application/json'])
server.setopt(server.TIMEOUT, 55)
server.setopt(server.POST,1)

slack = pycurl.Curl()
slack.setopt(slack.URL,settings.slackUrl)
slack.setopt(slack.HTTPHEADER,['Accept: application/json'])
slack.setopt(slack.TIMEOUT, 55)
slack.setopt(slack.POST,1)
slackTest = pycurl.Curl()
slackTest.setopt(slackTest.URL,settings.slackTestUrl)
slackTest.setopt(slackTest.HTTPHEADER,['Accept: application/json'])
slackTest.setopt(slackTest.POST,1)
slackTest.setopt(slackTest.TIMEOUT, 55)
slackTest.setopt(slackTest.WRITEDATA,buffer)

mailgun = pycurl.Curl()
mailgun.setopt(mailgun.URL,settings.mailgunUrl)
mailgun.setopt(mailgun.USERPWD, settings.mailgunUser)
mailgun.setopt(mailgun.HTTPHEADER,['Accept: application/json'])
mailgun.setopt(mailgun.POST,1)
mailgun.setopt(mailgun.TIMEOUT, 55)
mailgun.setopt(mailgun.WRITEDATA,buffer2)

#globals
hx = HX711(settings.weight_data, settings.weight_clock)
network_warning = False

# Create NeoPixel object with appropriate configuration.
# Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
leds = Adafruit_NeoPixel(settings.leds_count, settings.leds_pin, 800000, 10, False, 255, 0)
leds.begin()
blue_spin_on = True

def led_on(leds):#array [red,amber,green,blue]
    if leds[0]:
        GPIO.output(settings.red, settings.on)
    if leds[1]:
        GPIO.output(settings.amber, settings.on)
    if leds[2]:
        GPIO.output(settings.green, settings.on)
    if leds[3]:
        GPIO.output(settings.blue, settings.on)
    
def led_off(leds):#array [red,amber,green,blue]
    if leds[0]:
        GPIO.output(settings.red, settings.off)
    if leds[1]:
        GPIO.output(settings.amber, settings.off)
    if leds[2]:
        GPIO.output(settings.green, settings.off)
    if leds[3]:
        GPIO.output(settings.blue, settings.off)
    
def blue_spin(i = 0):
    global leds, blue_spin_on
    if blue_spin_on:
        threading.Timer(0.05, blue_spin, [(i+1)%leds.numPixels()]).start() # keep spinning every 50ms
    leds.setPixelColor((i-2)%leds.numPixels(), Color(64, 64, 64)) # dim white
    leds.setPixelColor((i-1)%leds.numPixels(), Color(64, 78, 128)) # blueish white
    leds.setPixelColor(i, Color(64, 90, 255)) # blue
    leds.setPixelColor((i+1)%leds.numPixels(), Color(64, 78, 255)) # blueish white
    leds.show()

def white():
    global leds, blue_spin_on
    blue_spin_on = False # stop timer
    for i in range(leds.numPixels()):
        leds.setPixelColor(i, Color(255,255,255))
    leds.show()

def green():
    global leds, blue_spin_on
    blue_spin_on = False # stop timer
    for i in range(leds.numPixels()):
        leds.setPixelColor(i, Color(0,255,0))
    leds.show()

def amber():
    global leds, blue_spin_on
    blue_spin_on = False # stop timer
    for i in range(leds.numPixels()):
        leds.setPixelColor(i, Color(255,200,0))
    leds.show()

def red():
    global leds, blue_spin_on
    blue_spin_on = False # stop timer
    for i in range(leds.numPixels()):
        leds.setPixelColor(i, Color(255,0,0))
    leds.show()


def ping():
    global network_warning
    threading.Timer(300.0, ping).start() # run ping function every 300
    timer = time.gmtime()
    ip = get_ip_address()
    print("button ping: "+ip+", "+time.strftime('%b %d %Y %H:%M:%S',timer)+" UTC")
    slackTest.setopt(slackTest.POSTFIELDS,'{"text":"ping from '+settings.location+' foodcam ('+ip+'): '+time.strftime('%b %d %Y %H:%M:%S',timer)+'"}')
    try:
        slackTest.perform()
        network_warning = False
        print('Ping to slack test: '+str(slackTest.getinfo(pycurl.RESPONSE_CODE)))
        network_warning = (slackTest.getinfo(pycurl.RESPONSE_CODE) != 200)
        if network_warning:
            error_flash()
            print("Ping issue: "+str(slackTest.getinfo(pycurl.RESPONSE_CODE)))
    except pycurl.error as e:
        network_warning = True
        error_flash()
        print('Error ping: '+str(e))
    

def blink():
    global network_warning, leds
    led_off([0,0,0,1]) #blue led off
    if network_warning:
        error_flash()
    time.sleep(2)
    led_on([0,0,0,1]) #blue led on
    threading.Timer(0.1, blink).start()

def error_flash():
    print('Error flash!!!')
    led_on([1,0,0,0]) #red led on
    time.sleep(0.1)
    led_off([1,0,0,0]) #red led off
    time.sleep(0.1)
    led_on([1,0,0,0]) #red led on
    time.sleep(0.1)
    led_off([1,0,0,0]) #red led off
    time.sleep(0.1)
    led_on([1,0,0,0]) #red led on
    time.sleep(0.1)
    led_off([1,0,0,0]) #red led off
    time.sleep(0.1)
    led_on([1,0,0,0]) #red led on
    time.sleep(0.1)
    led_off([1,0,0,0]) #red led off
    time.sleep(0.1)

def get_ip_address():
    global network_warning
    ip_address = '';
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8",80))
        network_warning = False
        ip_address = s.getsockname()[0]
        s.close()
        return ip_address
    except pycurl.error as e:
        network_warning = True
        error_flash()
        print('Error ip_address: '+str(e))

def upload_dropbox(filename):
    global network_warning
    try:
        os.system('bash /home/pi/FoodCam/dropbox_uploader.sh upload /home/pi/'+filename+' /')
        time.sleep(1)
        bashIO = os.popen('bash /home/pi/FoodCam/dropbox_uploader.sh share /'+filename).read()
        network_warning = False
        print('dropbox_uploader: '+bashIO)
        return bashIO.split('link: ')[1].replace('dl=0\n','raw=1')
    except: 
        network_warning = True
        error_flash()
        print('dropbox_uploader issue.')
    if bashIO == "":
        network_warning = True
        error_flash()
        print('dropbox_uploader empty: '+bashIO)
    

def send_server(url, weight):
    global network_warning
    data = {'recipient':settings.recipient,
            'weight':str(weight),
            'location':settings.location,
            'slackUrl':settings.slackUrl,
            'email_to':settings.email_to,
            'image_url':str(url)
    }
    print(data)
    js = json.dumps(data)
    server.setopt(server.HTTPHEADER, [ 'Content-Type: application/json' , 'Accept: application/json'])
    server.setopt(server.POSTFIELDS,js)
    try:
        server.perform()
        network_warning = False
        print('Sent to server: '+str(server.getinfo(pycurl.RESPONSE_CODE)))
    except pycurl.error as e:
        network_warning = True
        error_flash()
        print('Error server: '+str(e))

#weight sensor
def setup_weight():
    global hx
    hx.set_reading_format("MSB", "MSB")
    hx.set_reference_unit(170)#fc unit
    hx.reset()
    hx.tare()
    print "Zeroing weight done!"


def read_weight():
    w1 = hx.get_weight(settings.weight_data)
    hx.power_down()
    hx.power_up()
    time.sleep(0.05)
    w2 = hx.get_weight(settings.weight_data)
    hx.power_down()
    hx.power_up()
    time.sleep(0.05)
    w3 = hx.get_weight(settings.weight_data)
    hx.power_down()
    hx.power_up()
    time.sleep(0.05)
    w4 = hx.get_weight(settings.weight_data)
    hx.power_down()
    hx.power_up()
    time.sleep(0.05)
    w5 = hx.get_weight(settings.weight_data)
    hx.power_down()
    hx.power_up()
    time.sleep(0.05)
    avg_w = -1*(w1+w2+w3+w4+w5)/5
    print 'w avg: '+str(avg_w)
    return float(avg_w)/1000

#button press
def capture(channel):
    global network_warning, blue_spin_on
    now = time.time()
    led_on([1,0,0,0]) #red led on
    if settings.leds_enabled:
        white()
    print('Button Pressed, channel '+str(channel))
    time.sleep(1.1)
    try:
        weight = read_weight()
        weight_str = str(round(weight, 2))
        print('Weight captured: '+weight_str)
    except: 
        print('Error capturing weight')
    now1 = datetime.now() 
    date_time = now1.strftime("%Y-%m-%d_%H:%M:%S")
    filename = 'foodcam_image_'+date_time+'.jpg'
    print(filename)
    camera.capture('/home/pi/'+filename)
    print('A photo has been taken')
    time.sleep(0.6)
    led_off([1,0,0,0]) #red led off
    led_on([0,1,0,0]) #amber led on
    if settings.leds_enabled:
        amber()
    url = upload_dropbox(filename)
    if not url:
        error_flash()
        print('No image url, ending capture')
        led_off([0,1,0,0]) #amber led off
        return
    send_server(url, weight)
    led_off([0,1,0,0]) #amber led off
    led_on([0,0,1,0]) #green led on
    if settings.leds_enabled:
        green()
    later = time.time()
    capture_time = int(later - now)
    bounce_time = (29-capture_time) if capture_time<29 else 0.5
    print('Capture time: '+str(capture_time)+'. Green for '+str(bounce_time)+' seconds.')
    time.sleep(bounce_time)
    os.remove('/home/pi/'+filename) 
    led_off([0,0,1,0]) #green led off
    if settings.leds_enabled:
        blue_spin_on = True
        blue_spin()

#inits
setup_weight()
blue_spin()  # Blue wipe

# bounce must be greater than time to upload image and send to slack/email, eg 30 seconds
GPIO.add_event_detect(settings.button, GPIO.FALLING, callback=capture, bouncetime=60000)

#def exit():
#    GPIO.cleanup() #Clean up GPIO on CTRL+C exit


