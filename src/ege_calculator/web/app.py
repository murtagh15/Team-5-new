from flask import Flask
from .api_routes import api
from .ui_routes import ui

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.register_blueprint(ui)
    app.register_blueprint(api, url_prefix="/api")
    return app