import os

from flask import Flask, render_template, request, redirect
from tvleds import tvleds, utilities

# init AmbientLeds object
ambient_leds = AmbientLEDs()

app = Flask(__name__)

@app.route("/")
def main():
    return render_template('base.html', color=color)

@app.route("/fill", methods=['POST'])
def fill_color():
    color = request.form.get('fill_rgb')
    #print(color)
    r,g,b = hex2rgb(color)
    print('RGB: {0},{1},{2}'.format(r,g,b))
    ambient_leds.fill(i_red,i_green,i_blue)
    return redirect('/')
