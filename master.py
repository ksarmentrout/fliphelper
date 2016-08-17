# Standard Imports
import os

# Third party imports
from flask import Flask, render_template

# Create the app
app = Flask(__name__)
app.config.from_object('flask_config')

@app.route('/')
def homepage():
    return render_template('index.html')
