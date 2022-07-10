import picamera
import numpy as np
from tvleds import AmbientLEDs
from threading import Lock

# init AmbientLeds object
ambient_leds = AmbientLEDs()

class CameraOutput(object):
    def __init__(self):
        self.frame = np.zeros((640,480,3))
        self.lock = Lock()

    def write(self, buf):
        image = np.frombuffer(buf,dtype=np.uint8)

        self.lock.acquire()
        self.frame = image.reshape((640,480,3))
        self.lock.release()


with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
    output = CameraOutput()
    #Uncomment the next line to change your Pi's Camera rotation (in degrees)
    #camera.rotation = 90
    camera.start_recording(output, format='rgb')
    try:
        while True:
            output.lock.acquire()
            frame = output.frame 
            output.lock.release()

            r,g,b = frame[320,240,:]
            ambient_leds.fill(r,g,b)

    finally:
        camera.stop_recording()