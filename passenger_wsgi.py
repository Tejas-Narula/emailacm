import sys
import os

from a2wsgi import ASGIMiddleware
from main import app

sys.path.insert(0, os.path.dirname(__file__))

application = ASGIMiddleware(app)