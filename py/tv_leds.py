import board
import neopixel
import cv2
import sys
import time
from datetime import datetime
import numpy as np

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
    r = 255 * r/max_rgb
    g = 255 * g/max_rgb
    b = 255 * b/max_rgb

    return int(r), int(g), int(b)

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
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, self.frame_width)
        self.cap.set(4, self.frame_height)

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

    def mood(self, period = 15, time_step_s = 0.10):
        
        # status and fields to track while running
        status = True 
        done = True

        # get time step in us, determine number of steps per each period
        time_step_us = time_step_s * 1000000
        period_steps = int(period / time_step_s)
        count = 0

        # track hue, saturation, and intensity values over time
        curr_hue = 0         # 0 to 359 degrees
        curr_saturation = 0  # 0 to 255
        intensity = 0.9      # 0 to 1, hardcode intensity for simplicity

        # track current values and delta values
        step_hue = 0
        step_saturation = 0

        # start loop
        while status:
            # get current time
            start_time = datetime.now()

            # if on the last cycle, the target value was reached
            if done:
                # get random values for hue and saturation
                new_hue = np.random.randint(0,359)
                new_saturation = np.random.rand()

                # find "shortest path" to new hue
                # determine step size for current hue and saturation values
                if (new_hue - curr_hue) % 360 > 180: # change hue by decreasing hue degree
                    step_hue = (360 - ((new_hue - curr_hue) % 360))/period_steps
                else: # change hue by increasing hue degree
                    step_hue = ((new_hue - curr_hue) % 360)/period_steps

                step_saturation = (new_saturation - curr_saturation)/period_steps

                done = False
                count = 0

            # run step
            else:
                # change hue and saturation value by step
                curr_saturation = curr_saturation + step_saturation
                curr_hue = (curr_hue + step_hue) % 360

                # convert to rgb, then fill leds
                r,g,b = hsi2rgb(curr_hue,curr_saturation,intensity)
                self.fill(r,g,b)
                count = count + 1

                # if count is reached, get new HSI target value
                if count > period_steps:
                    done = True

                # get time elapsed and sleep for remaining time to match period
                duration = datetime.now() - start_time
                remaining_time = time_step_us - duration.microseconds

                time.sleep(remaining_time/1000000)



# start processing here
ambient_leds = AmbientLEDs()

num_args = len(sys.argv)

if num_args > 1:
    command = sys.argv[1]

    if command == 'test':
        ambient_leds.set_led(0,100,120,150)
        ambient_leds.set_led(1,230,100,80)

    elif command == 'clear':
        ambient_leds.clear_leds()

    elif command == 'fill':
        # detect arguments from command line and fill as that color
        if num_args >= 5:
            i_red = int(sys.argv[2])
            i_green = int(sys.argv[3])
            i_blue = int(sys.argv[4])

            ambient_leds.fill(i_red,i_green,i_blue)
        # just fill with red
        else:
            ambient_leds.fill(255,0,0)
        time.sleep(10)

    elif command == 'run':
        if ambient_leds.setup():
            print('Setup Complete')

        status = True
        while status:
            status = ambient_leds.task()

    elif command == 'mood':
        ambient_leds.mood()

    elif command == 'rainbow':
        for j in range(255):
            for i in range(ambient_leds.num_leds):
                pixel_index = (i * 256 // ambient_leds.num_leds) + j
                r,g,b = wheel(pixel_index & 255)
                ambient_leds.set_led(i,r,g,b)
            
            time.sleep(0.10)
else:
    print('No arguments passed')
