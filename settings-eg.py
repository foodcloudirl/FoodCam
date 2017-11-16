import RPi.GPIO as GPIO
slackUrl='https://hooks.slack.com/services/XXXXXXXXX/XXXXXXXXX/XXXXXXXXXXXXXXXXXXX'
slackTestUrl='https://hooks.slack.com/services/XXXXXXX/XXXXXXXXX/XXXXXXXXXXXXXXXXXXXX'
copiaUrl='https://copia.food.cloud'
copiaTestUrl='https://copia-c.food.cloud'
location='the kitchen'
recipient='FoodCloud'
on=GPIO.HIGH
off=GPIO.LOW

button=4

blue=17
red=18
amber=22
green=23

bakery=1
grocery=2
pantry=3
chilled=11
non_food=5

bakery_led=6
grocery_led=7
pantry_led=8
chilled_led=9
non_food_led=10
