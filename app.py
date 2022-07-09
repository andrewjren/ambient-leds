import os

from flask import Flask, render_template, request, redirect
from tvleds import AmbientLEDs

# init AmbientLeds object
ambient_leds = AmbientLEDs()

app = Flask(__name__)

@app.route("/")
def main():
    return render_template('base.html', color=ambient_leds.hex_color)

@app.route("/fill", methods=['POST'])
def fill_color():
    ambient_leds.hex_color = request.form.get('fill_rgb')
    #print(color)
    r,g,b = AmbientLEDs.hex2rgb(ambient_leds.hex_color)
    print('RGB: {0},{1},{2}'.format(r,g,b))
    ambient_leds.fill(r,g,b)
    return redirect('/')

@app.route("/mood", methods=['POST'])
def enable_mood():
    print('Mood Lighting Enabled!')
    return redirect('/')