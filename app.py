import os

from flask import Flask, render_template, request, redirect

# globals
color = '#0000ff'

app = Flask(__name__)

@app.route("/")
def main():
    global color 
    return render_template('base.html', color=color)

@app.route("/fill", methods=['POST'])
def fill_color():
    global color
    color = request.form.get('fill_rgb')
    print(color)
    return redirect('/')
