# Ambient LEDs

Ambient LEDs is a simple LED strip controller for a Raspberry Pi Zero W, heavily adapted from the existing
libraries available for Neopixel and PiCamera. It hosts a Flask web server as an interface so that you can
open a website from any phone or computer to change settings.

## Features

The TV LEDs python scripts are a controller for LED strips that are mounted to the back of a TV, similar to commercially
available LED strip controllers. 

* Ambient LED modes include Fill Colors (up to 4 colors), Mood Lighting, Pulse Lighting, Ambient Lighting 
  (requires a Pi Camera), and Rainbow Lighting. 
* Flask server allows for the Pi Zero W to be independently controlled, so you don't need an existing home automation
  server to use this. 
* Mood and Pulse Lighting provide sliders for the frequency/period.
* Passive Ambient LED lighting that matches what's displayed on the TV screen (no need to use an HDMI port).

## Demo Video

TBC

## How It Works

* Ambient Lighting uses a PiCamera to view the TV screen and change the color of the LEDs based on what's displayed on the screen.
  The approach for this is fairly naive due to latency concerns on the hardware. Basically, I just set regions of interest,
  and sample the image in between those regions of interest based on the number of LEDs on each side of the TV to determine
  what each LEDs color should be. This is heavily inspired by commercially available products.
* Mood Lighting randomly generates a new hue, and makes use of hue/saturation/intensity values to transition from the 
  current hue to the new hue. This means the mood lighting doesn't get any darker or brighter when transitioning between
  colors!
* The Flask server starts through `app.py`, which brings up the python classes for managing the camera and addressable LED strips. 
  Simple python multithreading is used to maintain access to the Flask server while also changing LED strip colors in the background. 

## Setup

I used WS2812B addressable LED strips with adhesive to attach to my TV, and 3D printed a small ball/socket mount for the 
Raspberry Pi Camera. I bought a standard 5V power supply for the LEDs, and soldered leads onto the Pi for external power, 
and the data line for the LED strips. 

This project uses Python 3.9.2. Python dependencies are listed in `requirements.txt` for a pip virtual environment. 

Be sure to enable the camera in `raspi-config`. 

## TODO/WIP

* Better configuration management (number of LEDs, toggling Pi Camera support on/off)
* Wiring Diagram
* Updating interfaces for re-use in other applications

## References

* https://learn.adafruit.com/neopixels-on-raspberry-pi/python-usage
* https://flask.palletsprojects.com/en/2.2.x/
* https://picamera.readthedocs.io/en/release-1.13/