#!/bin/sh

echo "FoodCam Setup: Setting up FoodCam on this Raspberry Pi! Please wait..."

# motion
sudo apt-get install motion
echo "FoodCam Setup: Camera software installed..."

# pycurl
sudo apt-get install python-pycurl
echo "FoodCam Setup: Code connectivity software installed..."

# button and settings
cp button-eg.sh ../button.sh
# rc.local update
sudo sed -i "s|fi|fi\n\nprintf \"**************************\"\nprintf \"STARTING FOODCLOUD FOODCAM\"\nprintf \"**************************\"\nsudo motion \&\nsudo sh /home/pi/button.sh \&\n;|g" /etc/rc.local
cp settings-eg.py settings.py
echo "FoodCam startup files copied..."

# load sensor
git clone https://github.com/tatobari/hx711py

# led ring
git clone https://github.com/jgarff/rpi_ws281x
cd rpi_ws281x/
sudo scons # install c libs
cd python
sudo python setup.py build
sudo python setup.py install
cd ../../  # back to ~/FoodCam

# load sensor



echo ""
echo "FoodCam Setup: Please edit settings.py to contain the correct credentials for setting up your FoodCloud device."
echo "FoodCam Setup: You can do this by typing 'sudo nano ~/FoodCam/settings.py' now."
echo ""
