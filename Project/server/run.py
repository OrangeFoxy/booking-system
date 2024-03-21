from db import connect
from routes import Router
from controllers import Controller
from werkzeug.serving import run_simple

app = Router(Controller(connect.connect()))
run_simple('localhost', 4000, app, use_reloader=True)