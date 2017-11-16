#!/bin/sh


# motion
sudo apt-get install motion

# button.sh
cp button-eg.sh ../button.sh


# rc.local update
NEWLINE=$'\n'
sed -i "s/exit=0/printf \"**************************\"${NEWLINE}printf \"STARTING FOODCLOUD FOODCAM\"${NEWLINE}printf \"**************************\"${NEWLINE}sudo motion &${NEWLINE}sudo sh /home/pi/button.sh &${NEWLINE}exit=0;/g" /etc/rc.local

echo "\a"