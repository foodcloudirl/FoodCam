#!/bin/sh
sudo python /home/pi/FoodCam/button.py >> /home/pi/button.log 2>&1 &
sudo sh /home/pi/FoodCam/network-monitor.sh >> /home/pi/network.log 2>&1 &

