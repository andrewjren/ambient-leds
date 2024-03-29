import os
import threading
from threading import Thread, Event
import time
from datetime import datetime
import picamera

from flask import Flask, render_template, request, redirect
from tvleds import *

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
def task_mood():
    global ambient_leds
    print('Beginning Mood Task...')
    
    # initialize mood mode
    ambient_leds.init_mood()

    # run task for mood
    while not stop_thread.is_set():
        # get current time
        start_time = datetime.now()

        # take step of mood
        ambient_leds.step_mood()

        # get time elapsed and sleep for remaining time to match period
        duration = datetime.now() - start_time
        remaining_time = ambient_leds.time_step_us - duration.microseconds

        time.sleep(remaining_time/1000000)
    
    print('Ending Mood Task...')

def task_pulse():
    global ambient_leds
    print('Beginning Pulse Task...')

    # initialize pulse mode
    ambient_leds.init_pulse()

    while not stop_thread.is_set():
        # get current time
        start_time = datetime.now()

        # take step of mood
        ambient_leds.step_pulse()

        # get time elapsed and sleep for remaining time to match period
        duration = datetime.now() - start_time
        remaining_time = ambient_leds.time_step_us - duration.microseconds

        time.sleep(remaining_time/1000000)

def task_ambient():
    global ambient_leds
    print('Beginning Ambient Task...')

    # initialize ambient mode
    #ambient_leds.init_ambient()

    with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
        camera.awb_mode='off'
        camera.awb_gains=(1.64,1.08)
        camera.start_recording(ambient_leds.camera_output, format='rgb')
        while not stop_thread.is_set():
            ambient_leds.step_ambient()

        camera.stop_recording()
        pass

def task_rainbow():
    global ambient_leds
    print('Beginning Rainbow Task...')

    while not stop_thread.is_set():
        # get current time
        start_time = datetime.now()

        # take step of mood
        ambient_leds.step_rainbow()

        # get time elapsed and sleep for remaining time to match period
        duration = datetime.now() - start_time
        remaining_time = ambient_leds.time_step_us - duration.microseconds

        time.sleep(0.001)
    

def begin_task(task, mood_period = 15, pulse_period_s = 1):
    global threads

    if task == 'mood':
        t = threading.Thread(name='Mood Thread', target=task_mood)
        t.start()
        threads.append(t)

    elif task == 'pulse':
        t = threading.Thread(name='Pulse Thread', target=task_pulse)
        t.start()
        threads.append(t)

    elif task == 'ambient':
        t = threading.Thread(name='Ambient Thread', target=task_ambient)
        t.start()
        threads.append(t)
    elif task == 'rainbow':
        t = threading.Thread(name='Rainbow Thread', target=task_rainbow)
        t.start()
        threads.append(t)
    else:
        print('Task not defined!')

# routes for website

@app.route("/")
def main():
    return render_template('base.html', fill_num=ambient_leds.fill_num, colors=ambient_leds.hex_colors, bpm=ambient_leds.pulse_bpm, mood_period=ambient_leds.mood_period)

@app.route("/fill", methods=['POST'])
def fill_color():
    trigger_thread_stop()

    ambient_leds.fill_num = int(request.form.get('fill_num'))

    # get all colors listed in form
    for idx in range(ambient_leds.fill_num):
        form_str = 'fill_rgb{:d}'.format(idx)
        ambient_leds.hex_colors[idx] = request.form.get(form_str)

    # fill entire length
    if ambient_leds.fill_num == 1:
        r,g,b = AmbientLEDs.hex2rgb(ambient_leds.hex_colors[0])
        print('RGB: {0},{1},{2}'.format(r,g,b))
        ambient_leds.fill(r,g,b)

    # split half/half
    else:
        print('Split LEDs by {0}'.format(ambient_leds.fill_num))
        ambient_leds.split_fill(ambient_leds.fill_num)

    return redirect('/')

@app.route("/mood", methods=['POST'])
def enable_mood():
    trigger_thread_stop()

    ambient_leds.mood_period = int(request.form.get('mood_period'))

    print('Mood Lighting Enabled!')

    begin_task('mood', mood_period=ambient_leds.mood_period)

    return redirect('/')

@app.route("/pulse", methods=['POST'])
def enable_pulse():
    trigger_thread_stop()
    ambient_leds.pulse_bpm = request.form.get('pulse_bpm')
    ambient_leds.pulse_period_s = 1 / (int(ambient_leds.pulse_bpm) / 60)

    print('Pulse Lighting Enabled!')

    begin_task('pulse')

    return redirect('/')

@app.route("/ambient", methods=['POST'])
def enable_ambient():
    trigger_thread_stop()
    print('Ambient Lighting Enabled!')

    begin_task('ambient')

    return redirect('/')

@app.route("/rainbow", methods=['POST'])
def enable_rainbow():
    trigger_thread_stop()
    print('Rainbow Thread Enabled@')

    begin_task('rainbow')

    return redirect('/')