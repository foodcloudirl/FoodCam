#!/bin/sh


# motion
sudo apt-get install motion

# pycurl
sudo apt-get install python-pycurl

# button and settings
cp button-eg.sh ../button.sh
cp settings-eg.sh settings.sh


# rc.local update
sed -i "s|fi|fi\n\nprintf \"**************************\"\nprintf \"STARTING FOODCLOUD FOODCAM\"\nprintf \"**************************\"\nsudo motion \&\nsudo sh /home/pi/button.sh \&\n;|g" /etc/rc.local

echo "\a Please edit settings.py to contain the correct credentials for setting up your FoodCloud device."