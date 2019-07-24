# FoodCloud-FoodCam

If you have surplus food to share with the office
put the food on the table
point the camera at it
press the button!

Everyone in the office will automatically get a picture of the food sent to them (via slack, if you don’t have it, get it…slack.com) to say there’s food available!



## Set up FoodCam

## Headless Setup of Pi
Download latest version of Raspian Jessie Lite from https://www.raspberrypi.org/downloads/raspbian/
Install Raspbian Jessie Lite on SD Card with Etcher

Create blank file called 'ssh' and add to boot partition
Create file called 'wpa_supplicant.conf' with the network details (like shown below) and add to boot partition
OR
Turn on the Pi with a pre-loaded OS, preferabably some Raspian flavour
With a monitor and keyboard connected, sudo nano /etc/wpa_supplicant/wpa_supplicant.conf to have the network details:
```
network={
    ssid="NETWORK NAME"
    psk="PASSWORD"
    key_mgmt=WPA-PSK
}
```

# 1st boot
Locate On Network, default hostname is raspberrypi
``` sudo passwd```
 Follow Instructions to change password


# Change raspi-config 
Set up picamera
```sudo raspi-config```
Follow dialog to enable camera and change hostname to foodcam, enable raspicam and ssh

# Clone the github folder to the raspi
```
cd ~
git clone THE_URL_OF_THIS_REPO
cd FoodCam
```


# Run the setup shell script
```sudo sh setup.sh```

# Update the settings for your surplusfoodcam

Due to the various ways possible to build these surplus food cameras, we have created an ignored file for you to manage your sensitive credentials and specific settings. DO NOT COMMIT SETTINGS TO UNIGNORED FILES!
```
cd FoodCam
sudo nano settings.py
```
Change the settings according to the GPIO pins you're using for the buttons, leds and peripherals
Specify the integration details used to talk to your communication systems

![alt text](https://www.dropbox.com/s/6g68ddew4pxcves/foodcam_image_2019-07-19_01%3A41%3A59.jpg?raw=1 "FoodCam LEDs and Button wiring")


# Contributions
Please feel free to get in contact twitter.com/surplusfoodcam
Submit issues on github or pull requests directly to the repo.
Please ensure all code is of high quality and robust so that errors etc can be managed gracefully.





# Older setup, for usb cameras for example:

# Update Image, Install motion
```
sudo apt-get update
sudo apt-get upgrade
```
Make some coffee - takes a bit of time!
```sudo apt-get install motion```

# Set motion to run at boot

```sudo nano /etc/rc.local```
# place code before exit=0:
```
    printf "**************************"
    printf "STARTING FOODCLOUD FOODCAM"
    printf "**************************"
    sudo motion &
    sudo sh /home/pi/button.sh &
```
and update motion
```
sudo nano /etc/default/motion
#set to no
```
# Update motion.conf
```
sudo nano /etc/motion/motion.conf
daemon on
width 1024
height 576
output_pictures off
ffmpeg_output_movies off
target_dir /home/pi/motion
stream motion on
stream_localhost off
```



