from __future__ import print_function
from flask import Flask, render_template, g, jsonify, session, request
from flaskext.mysql import MySQL
import yaml
import sys
import inspect
from os import path, environ
from . import empty


flora_portal_path = environ['FLORA_PORTAL_PATH']

app = Flask(__name__, static_folder=path.join(flora_portal_path, 'static'))

try:
    with open(path.expanduser('~/.config/flora_portal.yml')) as config_file:
        config = yaml.safe_load(config_file)
except IOError:
    app.logger.error("Failed to read ~/.config/flora_portal.yml")
else:
    try:
        app.secret_key = config['secret_key']
    except KeyError:
        app.logger.warning("No secret key provided")

    try:
        db_config = config['database']
    except KeyError:
        app.logger.warning("No database configuration provided")

    try:
        app.config['MYSQL_DATABASE_DB'] = db_config['db']
    except KeyError:
        app.logger.warning("No database provided")

    app.config['MYSQL_DATABASE_USER'] = db_config.get('user')
    app.config['MYSQL_DATABASE_PASSWORD'] = db_config.get('password')
    app.config['MYSQL_DATABASE_HOST'] = db_config.get('host')
    app.config['MYSQL_DATABASE_PORT'] = db_config.get('port')

mysql = MySQL(autocommit=True)
mysql.init_app(app)

directory = path.dirname(inspect.getfile(empty))
app.config['TAXA_IMG_DIR'] = path.join(directory, 'static/taxa_img')
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg'])


from .views import *

if __name__ == "__main__":
    app.run(host='')

