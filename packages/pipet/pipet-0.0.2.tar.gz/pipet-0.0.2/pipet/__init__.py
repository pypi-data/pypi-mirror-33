# -*- coding: utf-8 -*-
import logging
import os
import sys

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf.csrf import CSRFProtect
from raven.contrib.flask import Sentry
from raven.contrib.celery import register_logger_signal, register_signal
from sqlalchemy import Column

import settings


def create_app():
    from pipet.models import db

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'POSTGRES_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SERVER_NAME'] = os.getenv('SERVER_NAME', None)
    app.config['PREFERRED_URL_SCHEME'] = os.getenv('PREFERRED_URL_SCHEME')
    app.config['GOOGLE_PICKER_API_KEY'] = os.getenv(
        'GOOGLE_PICKER_API_KEY')
    app.config['WEBPACK_MANIFEST_PATH'] = 'static/build/manifest.json'
    app.secret_key = os.getenv('FLASK_SECRET_KEY')

    csrf = CSRFProtect()
    login_manager = LoginManager()
    sentry = Sentry(logging=True, level=logging.ERROR, wrap_wsgi=True)

    csrf.init_app(app)
    db.init_app(app)
    migrate = Migrate(app, db)
    sentry.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'index'

    from pipet.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

    from pipet.views import blueprint  # NOQA

    app.register_blueprint(blueprint)

    from pipet import cli  # NOQA

    # from pipet.api.views import blueprint as api_blueprint

    # app.register_blueprint(api_blueprint, url_prefix='/api')

    from pipet.sources.zendesk import ZendeskAccount
    from pipet.sources.zendesk.views import blueprint as zendesk_blueprint
    from pipet.sources.zendesk.tasks import sync as zendesk_sync_all

    app.register_blueprint(zendesk_blueprint, url_prefix='/zendesk')

    from pipet.sources.stripe import StripeAccount
    from pipet.sources.stripe.views import blueprint as stripe_blueprint

    app.register_blueprint(stripe_blueprint, url_prefix='/stripe')

    return app
