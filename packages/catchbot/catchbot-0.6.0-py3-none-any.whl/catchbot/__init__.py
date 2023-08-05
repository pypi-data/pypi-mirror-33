from flask import Flask

from .router_bot import RouterBot
from .routes import register_routes

__version__ = '0.0.2'

app = Flask(__name__)
register_routes(app)
