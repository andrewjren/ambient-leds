import board
import neopixel
import picamera
import sys
import time
from datetime import datetime
import numpy as np
from threading import Event, Lock
import math

# CameraOutput manages the output buffer of the camera
class CameraOutput(object):
    def __init__(self, frame_width, frame_height):
        self.frame = np.zeros((frame_width,frame_height,3))
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.lock = Lock()

    def write(self, buf):
        image = np.frombuffer(buf,dtype=np.uint8)

        self.lock.acquire()
        self.frame = image.reshape((self.frame_width,self.frame_height,3))
        self.lock.release()

# AmbientLEDs defines and controls the LED Strips and Camera 
class AmbientLEDs:

    def __init__(self):
        
        # Configuration Fields

        # LED Config
        self.num_ver = 20  # number of LEDs on left/right side
        self.num_hor = 35 # number of LEDs on top/bottom side
        self.num_leds = 2 * self.num_ver + self.num_hor # total number of LEDs

        # gamma shift table
        self.gamma_table = [  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,
                              0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  1,  1,  1,
                              1,  1,  1,  1,  1,  1,  1,  1,  1,  2,  2,  2,  2,  2,  2,  2,
                              2,  3,  3,  3,  3,  3,  3,  3,  4,  4,  4,  4,  4,  5,  5,  5,
                              5,  6,  6,  6,  6,  7,  7,  7,  7,  8,  8,  8,  9,  9,  9, 10,
                             10, 10, 11, 11, 11, 12, 12, 13, 13, 13, 14, 14, 15, 15, 16, 16,
                             17, 17, 18, 18, 19, 19, 20, 20, 21, 21, 22, 22, 23, 24, 24, 25,
                             25, 26, 27, 27, 28, 29, 29, 30, 31, 32, 32, 33, 34, 35, 35, 36,
                             37, 38, 39, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 50,
                             51, 52, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 66, 67, 68,
                             69, 70, 72, 73, 74, 75, 77, 78, 79, 81, 82, 83, 85, 86, 87, 89,
                             90, 92, 93, 95, 96, 98, 99,101,102,104,105,107,109,110,112,114,
                            115,117,119,120,122,124,126,127,129,131,133,135,137,138,140,142,
                            144,146,148,150,152,154,156,158,160,162,164,167,169,171,173,175,
                            177,180,182,184,186,189,191,193,196,198,200,203,205,208,210,213,
                            215,218,220,223,225,228,231,233,236,239,241,244,247,249,252,255]

        # Pi Config
        self.led_port = board.D18 # raspberry pi port that LEDs are controlled off of
        self.pixels = neopixel.NeoPixel(self.led_port, self.num_leds) # object for controlling LED strips

        # Camera Config
        self.frame_width = 640
        self.frame_height = 480
        self.resolution = '{0:d}x{1:d}'.format(self.frame_width,self.frame_height)
        self.framerate = 24
        self.camera = picamera.PiCamera(resolution='640x480', framerate=24)
        self.camera_output = CameraOutput(self.frame_width, self.frame_height)

        # Flask Config
        self.hex_color = "#0000FF"

        # Generic LED Values
        self.curr_hue = 0         # 0 to 359 degrees
        self.curr_saturation = 0  # 0 to 255
        self.curr_intensity = 0.9 # 0 to 1, hardcode intensity for simplicity

        # Mood Config
        self.mood_cycle_done = True
        self.mood_period_steps = 10
        self.mood_count = 0
        self.mood_time_step_us = 0
        self.step_hue = 0
        self.step_saturation = 0

        # Pulse Config
        self.pulse_time_step_us = 0
        self.pulse_period_steps = 0
        self.pulse_period_s = 0
        self.pulse_count = 0

        # Ambient Config
        self.ambient_rois = np.array([[160,360],[160,120],[480,180],[480,300]])
        self.ambient_num_rois = self.ambient_rois.shape()[0]

    # gamma shift RGB values based on gamma table
    def gamma_shift(self, in_red, in_green, in_blue):
        red = self.gamma_table[in_red]
        green = self.gamma_table[in_green]
        blue = self.gamma_table[in_blue]

        return red, green, blue

    # set color of an LED with gamma shift
    def set_led(self, index, in_red, in_green, in_blue):

        # gamma shift input rgb values
        red, green, blue = self.gamma_shift(in_red, in_green, in_blue)

        # set single pixel
        self.pixels[index] = (red, green, blue)

    # set color of all LEDs with gamma shift
    def fill(self, in_red, in_green, in_blue):

        # gamma shift input rgb values
        red, green, blue = self.gamma_shift(in_red, in_green, in_blue)

        # set all pixels
        self.pixels.fill((red, green, blue))

    # set all LEDs to be dark
    def clear_leds(self):
        self.pixels.fill((0,0,0))

    # 
    def setup(self):
        if self.cap.isOpened():
            time.sleep(2)
            return True
        else:
            print('Failed Camera Capture Opening')
            return False

    def task(self):
        # read camera
        success, img = self.cap.read()
        if success:
            # sample image pixels at key points
            sample_points_idx_1 = np.linspace(0,self.frame_height-1,self.num_ver,dtype=np.int16)
            
            key_points = img[sample_points_idx_1,320,:]

            led_idx = 0
            for kp in key_points:
                self.set_led(led_idx,kp[2],kp[1],kp[0])
                led_idx = led_idx + 1

            return True 
        else:
            print('Failed Camera Frame Read')
            return False 

    # init mood mode 
    def init_mood(self, period = 15, time_step_s = 0.10, intensity = 0.9):
        # reset tracker for when current color cycle is done
        self.mood_cycle_done = True
        self.mood_count = 0

        # get time step in us, determine number of steps per each period
        self.mood_time_step_us = time_step_s * 1000000
        self.mood_period_steps = int(period / time_step_s)

        # other configuration
        self.curr_intensity = intensity

        print('Initialize Mood mode with period = {0}, time step = {1}'.format(period,time_step_s))
        
    # step mood mode
    # meant to be a single step that is managed by another process
    def step_mood(self):
    
        # if on the last cycle, the target value was reached
        if self.mood_cycle_done:
            # get random values for hue and saturation
            new_hue = np.random.randint(0,359)
            new_saturation = np.random.rand()

            # find "shortest path" to new hue
            # determine step size for current hue and saturation values
            if (new_hue - self.curr_hue) % 360 > 180: # change hue by decreasing hue degree
                self.step_hue = (360 - ((new_hue - self.curr_hue) % 360))/self.mood_period_steps
            else: # change hue by increasing hue degree
                self.step_hue = ((new_hue - self.curr_hue) % 360)/self.mood_period_steps

            self.step_saturation = (new_saturation - self.curr_saturation)/self.mood_period_steps

            self.mood_cycle_done = False
            self.mood_count = 0

        # run step
        else:
            # change hue and saturation value by step
            self.curr_saturation = self.curr_saturation + self.step_saturation
            self.curr_hue = (self.curr_hue + self.step_hue) % 360

            # convert to rgb, then fill leds
            r,g,b = self.hsi2rgb(self.curr_hue,self.curr_saturation,self.curr_intensity)
            self.fill(r,g,b)
            self.mood_count = self.mood_count + 1

            # if count is reached, get new HSI target value
            if self.mood_count > self.mood_period_steps:
                self.mood_cycle_done = True

   # init pulse mode 
    def init_pulse(self, period_s, time_step_s):

        # get time step in us, determine number of steps per each period
        self.pulse_period_s = period_s
        self.pulse_time_step_us = time_step_s * 1000000
        self.pulse_period_steps = int(period_s / time_step_s)

        print('Initialize Pulse mode with period = {0}, time step = {1}'.format(period_s,time_step_s))

    # step pulse mode
    def step_pulse(self):

        # temp: set hue and saturation
        self.curr_hue = 0
        self.curr_saturation = 255

        # get current time t
        t = self.pulse_time_step_us * self.pulse_count

        # get lambda l, based on period of pulse
        l = 2 / self.pulse_period_s

        self.curr_intensity = math.exp(-l*t)

        print('Pulse HSI: {0},{1},{2}'.format(self.curr_hue,self.curr_saturation,self.curr_intensity))

        # convert to rgb, then fill leds
        r,g,b = self.hsi2rgb(self.curr_hue,self.curr_saturation,self.curr_intensity)
        print('Pulse RGB: {0},{1},{2}'.format(r,g,b))
        self.fill(r,g,b)

        self.pulse_count = self.pulse_count + 1

        # if finished with pulse period
        if self.pulse_count > self.pulse_period_steps:
            self.pulse_count = 0

    # init ambient mode
    def init_ambient(self):
        self.camera.start_recording(self.camera_output, format='rgb')

    # step ambient mode
    def step_ambient(self):
        self.camera_output.lock.acquire()
        frame = self.camera_output.frame 
        self.camera_output.lock.release()

        rgb_values = []

        for roi in self.ambient_rois:
            rgb = frame[roi[0],roi[1],:]

            rgb_values.append(int(rgb))

        leds_per_roi = int(self.num_leds/self.ambient_num_rois)

        for led_idx in range(self.num_leds):
            roi_idx = math.floor(led_idx/leds_per_roi)
            rgb = rgb_values[roi_idx]
            self.set_led(led_idx, rgb[0], rgb[1], rgb[2])



    @staticmethod
    def hsi2rgb(H,S,I):

        # convert HSI to RGB
        if H == 0:
            r = I + 2*I*S
            g = I - I*S
            b = I - I*S

        elif H < 120:
            r = I + I*S*np.cos(H*np.pi/180)/np.cos((60-H)*np.pi/180)
            g = I + I*S*(1-np.cos(H*np.pi/180)/np.cos((60-H)*np.pi/180))
            b = I - I*S

        elif H == 120:
            r = I - I*S
            g = I + 2*I*S
            b = I - I*S 

        elif H < 240:
            r = I - I*S 
            g = I + I*S*np.cos((H-120)*np.pi/180)/np.cos((180-H)*np.pi/180)
            b = I + I*S*(1 - np.cos((H-120)*np.pi/180)/np.cos((180-H)*np.pi/180))

        elif H == 240:
            r = I - I*S 
            g = I - I*S 
            b = I + 2*I*S 

        else:
            r = I + I*S*(1 - np.cos((H-240)*np.pi/180)/np.cos((300-H)*np.pi/180))
            g = I - I*S 
            b = I + I*S*np.cos((H-240)*np.pi/180)/np.cos((300-H)*np.pi/180) 

        max_rgb = np.max([r,g,b])
        r = max(255 * r/max_rgb,0)
        g = max(255 * g/max_rgb,0)
        b = max(255 * b/max_rgb,0)

        return int(r), int(g), int(b)

    # hex rgb string has format: #000000
    @staticmethod
    def hex2rgb(hex_string):
        r = int(hex_string[1:3], 16)
        #print('hex r value = {0}, true r value = {1}'.format(hex_string[1:2],r))
        g = int(hex_string[3:5], 16)
        b = int(hex_string[5:7], 16)

        return r,g,b


    @staticmethod
    def wheel(pos):
        # Input a value 0 to 255 to get a color value.
        # The colours are a transition r - g - b - back to r.
        if pos < 0 or pos > 255:
            r = g = b = 0
        elif pos < 85:
            r = int(pos * 3)
            g = int(255 - pos * 3)
            b = 0
        elif pos < 170:
            pos -= 85
            r = int(255 - pos * 3)
            g = 0
            b = int(pos * 3)
        else:
            pos -= 170
            r = 0
            g = int(pos * 3)
            b = int(255 - pos * 3)
        return (r, g, b)

