import os
import sys
import traceback
from os.path import join
import logging
from urllib import unquote_plus
from flask import jsonify, send_from_directory, request, redirect, send_file, Flask
from flask.ext.login import login_user, logout_user, current_user, login_required
from flask_login import LoginManager

from syncloudlib import logger
from syncloudlib.json import convertible

from syncloud_files.ldapauth import authenticate
from syncloud_files.flask_decorators import nocache
from syncloud_files.models import User, FlaskUser
from syncloud_files.config import BrowserConfig
from syncloud_files.browser import Browser


def create_web_app(data_dir):
    config = BrowserConfig(data_dir)

    logger.init(logging.INFO, False, join(config.get_browser_log()))

    browser = Browser(config)

    app = Flask(__name__)
    app.config['SECRET_KEY'] = config.get_web_secret_key()
    login_manager = LoginManager()
    login_manager.init_app(app)


    html_prefix = ''
    rest_prefix = '/rest'


    @login_manager.unauthorized_handler
    def _callback():
        if request.is_xhr:
            return 'Unauthorised', 401
        else:
            return redirect(html_prefix + '/login.html')


    @app.route(html_prefix + '/<path:filename>')
    @nocache
    def static_file(filename):
        return send_from_directory(config.www_root(), filename)


    @login_manager.user_loader
    def load_user(email):
        return FlaskUser(User(email))


    @app.route(rest_prefix + "/login", methods=["GET", "POST"])
    def login():

        if 'name' in request.form and 'password' in request.form:
            try:
                authenticate(request.form['name'], request.form['password'])
                user_flask = FlaskUser(User(request.form['name']))
                login_user(user_flask, remember=False)
                # next_url = request.get('next_url', '/')
                return redirect("/")
            except Exception, e:
                traceback.print_exc(file=sys.stdout)
                return jsonify(message=e.message), 400

        return jsonify(message='missing name or password'), 400


    @app.route(rest_prefix + "/logout", methods=["POST"])
    @login_required
    def logout():
        logout_user()
        return 'User logged out', 200


    @app.route(rest_prefix + "/user", methods=["GET"])
    @login_required
    def user():
        return jsonify(convertible.to_dict(current_user.user)), 200


    @app.route('/')
    @login_required
    def index():
        return static_file('index.html')

    files_prefix = rest_prefix + '/files/'

    @nocache
    @app.route(files_prefix)
    @app.route(files_prefix + '<path:path>')
    @login_required
    def browse(path=''):
        filesystem_path = join('/', unquote_plus(path))
        if os.path.isfile(filesystem_path):
            return send_file(filesystem_path, mimetype='text/plain')
        else:
            return jsonify(items=browser.browse(filesystem_path), dir=filesystem_path)


    @app.errorhandler(Exception)
    def handle_exception(error):
        print '-'*60
        traceback.print_exc(file=sys.stdout)
        print '-'*60
        response = jsonify(success=False, message=error.message)
        status_code = 500
        return response, status_code

    return app
