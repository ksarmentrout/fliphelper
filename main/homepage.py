# Standard Imports
import os

# Third party imports
from flask import Flask

# Create the app
app = Flask(__name__)
app.config.from_object(__name__)

