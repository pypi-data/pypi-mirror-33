from typing import Callable, cast, Union
from flask import Flask, Blueprint, request

from depytg.types import Update


def get_app(name: str, url_path: str, on_update: Callable[[Update], None]):
    """
    Returns a Flask app that calls `on_update` when new updates are received from Telegram.
    Webhook is reachable at /<url_path>/

    :param name: (str) Application name, use Python naming conventions
    :param url_path: (str) URL path
    :param on_update: (callable(Update)) Callable to be called on new updates
    :return: A new Flask app
    """
    app = Flask(name)

    get_blueprint(name, url_path, on_update, app)


def get_blueprint(name: str, url_path: str, on_update: Callable[[Update], None], bp: Union[Flask, Blueprint] = None):
    """
    Returns a Flask blueprint that calls `on_update` when new updates are received from Telegram.
    Webhook is reachable at /<mountpoint>/<url_path>/

    :param name: (str) Blueprint name, use Python naming conventions
    :param url_path: (str) URL path
    :param on_update: (callable(Update)) Callable to be called on new updates
    :param bp: Optional. An existing blueprint or Flask app to set up routes on instead of a new one. If not specified,
    a new blueprint will be created.
    :return: A blueprint
    """
    if not bp:
        bp = Blueprint(name, name)

    @bp.route("/{}/".format(url_path), methods=['POST'])
    def webhook():
        j = request.json
        on_update(cast(Update, Update.from_json(j)))
        return '', 200

    return bp
