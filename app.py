import os
import threading
from threading import Thread, Event
import time
from datetime import datetime
import picamera

from flask import Flask, render_template, request, redirect
from tvleds import AmbientLEDs, CameraOutput

# init AmbientLeds object
ambient_leds = AmbientLEDs()

app = Flask(__name__)

# Threading Setup
threads = []

# use as signal to stop threads
stop_thread = Event() 

# trigger thread stop
def trigger_thread_stop():
    global threads

    print('Stopping all Threads...')
    
    stop_thread.set()

    #for t in threads:
    #    t.join()
    while len(threads) > 0:
        t = threads.pop()
        t.join()

    stop_thread.clear()

# task_mood manages the calls to ambient_leds.mood()
def task_mood(period = 15, time_step_s = 0.10):
    global ambient_leds
    print('Beginning Mood Task...')
    
    # initialize mood mode
    ambient_leds.init_mood(period=period, time_step_s=time_step_s)

    # run task for mood
    while not stop_thread.is_set():
        # get current time
        start_time = datetime.now()

        # take step of mood
        ambient_leds.step_mood()

        # get time elapsed and sleep for remaining time to match period
        duration = datetime.now() - start_time
        remaining_time = ambient_leds.mood_time_step_us - duration.microseconds

        time.sleep(remaining_time/1000000)
    
    print('Ending Mood Task...')

def task_pulse(period_s = 1, time_step_s = 0.05):
    global ambient_leds
    print('Beginning Pulse Task...')

    # initialize pulse mode
    ambient_leds.init_pulse(period_s=period_s, time_step_s=time_step_s)

    while not stop_thread.is_set():
        # get current time
        start_time = datetime.now()

        # take step of mood
        ambient_leds.step_pulse()

        # get time elapsed and sleep for remaining time to match period
        duration = datetime.now() - start_time
        remaining_time = ambient_leds.pulse_time_step_us - duration.microseconds

        time.sleep(remaining_time/1000000)

def task_ambient():
    global ambient_leds
    print('Beginning Ambient Task...')

    # initialize ambient mode
    #ambient_leds.init_ambient()

    with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
        camera.start_recording(ambient_leds.camera_output, format='rgb')
        while not stop_thread.is_set():
            ambient_leds.step_ambient()

        camera.stop_recording()
        pass

    

def begin_task(task, mood_period = 15, mood_time_step_s = 0.10, pulse_period_s = 1):
    global threads

    if task == 'mood':
        t = threading.Thread(name='Mood Thread', target=task_mood, args=(mood_period, mood_time_step_s))
        t.start()
        threads.append(t)

    elif task == 'pulse':
        pulse_step_s = 0.05
        t = threading.Thread(name='Pulse Thread', target=task_pulse, args=(pulse_period_s,pulse_step_s))
        t.start()
        threads.append(t)

    elif task == 'ambient':
        t = threading.Thread(name='Ambient Thread', target=task_ambient)
        t.start()
        threads.append(t)
    else:
        print('Task not defined!')

# routes for website

@app.route("/")
def main():
    return render_template('base.html', color=ambient_leds.hex_color, bpm=ambient_leds.pulse_bpm)

@app.route("/fill", methods=['POST'])
def fill_color():
    trigger_thread_stop()
    ambient_leds.hex_color = request.form.get('fill_rgb')
    #print(color)
    r,g,b = AmbientLEDs.hex2rgb(ambient_leds.hex_color)
    print('RGB: {0},{1},{2}'.format(r,g,b))
    ambient_leds.fill(r,g,b)
    return redirect('/')

@app.route("/mood", methods=['POST'])
def enable_mood():
    trigger_thread_stop()
    print('Mood Lighting Enabled!')

    begin_task('mood')

    return redirect('/')

@app.route("/pulse", methods=['POST'])
def enable_pulse():
    trigger_thread_stop()
    ambient_leds.pulse_bpm = request.form.get('pulse_bpm')
    pulse_period_s = 1 / (int(ambient_leds.pulse_bpm) / 60)

    print('Pulse Lighting Enabled!')

    begin_task('pulse', pulse_period_s=pulse_period_s)

    return redirect('/')

@app.route("/ambient", methods=['POST'])
def enable_ambient():
    trigger_thread_stop()
    print('Ambient Lighting Enabled!')

    begin_task('ambient')

    return redirect('/')
