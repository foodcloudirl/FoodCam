#!/bin/sh


# motion
sudo apt-get install motion

# pycurl
sudo apt-get install python-pycurl

# button.sh
cp button-eg.sh ../button.sh


# rc.local update
NEWLINE=$'\n'
sed -i "s|fi|fi\n\nprintf \"**************************\"\nprintf \"STARTING FOODCLOUD FOODCAM\"\nprintf \"**************************\"\nsudo motion \&\nsudo sh /home/pi/button.sh \&\n;|g" /etc/rc.local

echo "\a"