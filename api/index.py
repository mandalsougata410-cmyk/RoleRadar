import os
import sys

# Ensure root folder is on Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

# Vercel looks for the ASGI application object
app = app
