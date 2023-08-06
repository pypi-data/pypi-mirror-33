import fnmatch
import logging
import os
import re
import sys
from datetime import timedelta
from importlib import import_module
from importlib.util import module_from_spec, spec_from_file_location
from pkgutil import get_loader
from traceback import format_exc

import boto3
from bjoern import run
from flask import Flask, jsonify
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, get_jwt_identity
from postgres import Postgres

from .constants import LOG_FORMAT, LOG_FORMAT_MSEC, TOKEN_HAS_EXPIRED

log = logging.getLogger(__name__)


class GnarApp:

    def __init__(
            self,
            name,
            production,
            port,
            env_prefix='GNAR',
            log_level=None,
            blueprint_modules=None,
            no_db=False,
            no_jwt=False):

        self.name = name
        self.display_name = name.title().replace('_', '')
        self.production = production
        self.port = port
        self.env_prefix = env_prefix
        self.log_level = log_level
        self.blueprint_modules = blueprint_modules
        self.no_db = no_db
        self.no_jwt = no_jwt

    def env(self, name, default=''):
        return os.getenv('{}_{}'.format(self.env_prefix, name), default)

    def get_ses_client(self):
        return boto3.client(
            'ses',
            region_name=self.env('SES_REGION_NAME'),
            aws_access_key_id=self.env('SES_ACCESS_KEY_ID'),
            aws_secret_access_key=self.env('SES_SECRET_ACCESS_KEY'))

    def preconfig(self):
        pass

    def configure_flask(self):
        self.flask = Flask(self.name)

    def configure_logger(self):
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter(self.env('LOG_FORMAT', LOG_FORMAT))
        formatter.default_msec_format = self.env('LOG_FORMAT_MSEC', LOG_FORMAT_MSEC)
        ch.setFormatter(formatter)
        root = logging.getLogger()
        root.addHandler(ch)
        logging.getLogger('boto').setLevel(logging.WARNING)
        project_env = '{}_LOG_LEVEL'.format(self.name.upper())
        log_level = self.log_level or self.env(project_env) or self.env('LOG_LEVEL', 'INFO')
        root.setLevel(log_level)

        log.info('Logging at {}'.format(log_level))

    def configure_bcrypt(self):
        # Generate a bcrypt singleton
        self.bcrypt = Bcrypt(self.flask)

    def configure_database(self):
        if not self.no_db:
            endpoint = self.env('PG_ENDPOINT')
            database = self.env('PG_DATABASE')
            username = self.env('PG_USERNAME')
            password = self.env('PG_PASSWORD')
            self.db = Postgres('host={} dbname={} user={} password={}'.format(endpoint, database, username, password))

    def attach_instance(self):
        main = import_module('{}.app.main'.format(self.name))
        main.app = self

    def configure_blueprints(self):
        if self.blueprint_modules:
            blueprint_modules = \
                self.blueprint_modules if isinstance(self.blueprint_modules, list) else [self.blueprint_modules]
            for blueprint_module in blueprint_modules:
                template = '{}.app.{}' if '.' in blueprint_module else '{}.app.{}.apis'
                module_name = template.format(self.name, blueprint_module)
                log.info(module_name)
                blueprint = import_module(module_name).blueprint
                self.flask.register_blueprint(blueprint)
                log.info('Listening on {}'.format(blueprint.url_prefix))
        else:
            path = os.path.dirname(get_loader(self.name).path)
            for root, dirnames, filenames in os.walk(os.path.join(path, 'app')):
                for filename in fnmatch.filter(filenames, '*.py'):
                    module_path = re.sub(r'(^{}|\.py$)'.format(os.path.join(root, filename)), '', filename)
                    module_name = '{}.{}'.format(self.name, re.sub(r'[\/]', '.', module_path))
                    spec = spec_from_file_location(module_name, os.path.join(root, filename))
                    module = module_from_spec(spec)
                    spec.loader.exec_module(module)
                    if hasattr(module, 'blueprint'):
                        self.flask.register_blueprint(module.blueprint)
                        log.info('Listening on {}'.format(module.blueprint.url_prefix))

    def configure_errorhandler(self):
        @self.flask.errorhandler(Exception)
        def error_handler(exp):
            error = '{} API Error'.format(self.display_name)
            traceback = '{}:\n{}'.format(error, format_exc())
            log.error(traceback)
            return jsonify({'error': error, 'traceback': traceback})

    def configure_jwt(self):
        if not self.no_jwt:
            exp_minutes = self.env('JWT_ACCESS_TOKEN_EXPIRES_MINUTES')
            self.flask.config['JWT_ACCESS_TOKEN_EXPIRES'] = \
                timedelta(minutes=int(exp_minutes) if exp_minutes.isdigit() else 15)
            self.flask.config['JWT_SECRET_KEY'] = self.env('JWT_SECRET_KEY')

            self.jwt = JWTManager(self.flask)

            @self.jwt.expired_token_loader
            def expired_token_callback():
                return jsonify({'error': TOKEN_HAS_EXPIRED})

            @self.jwt.invalid_token_loader
            def invalid_token_callback(error):
                return jsonify({'error': error})

            @self.jwt.unauthorized_loader
            def unauthorized_callback(error):
                return jsonify({'error': error})

    def configure_after_request(self):
        @self.flask.after_request
        def after_request(response):
            if not self.production:
                response.headers['Access-Control-Allow-Origin'] = '*'
                response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT'
                response.headers['Access-Control-Allow-Headers'] = 'Authorization'
                response.headers['Access-Control-Expose-Headers'] = 'Authorization'
            if not self.no_jwt:
                identity = get_jwt_identity()
                if identity:
                    response.headers['Authorization'] = 'Bearer {}'.format(create_access_token(identity=identity))
            return response

    def postconfig(self):
        pass

    def run(self):

        self.preconfig()

        self.configure_flask()

        self.configure_logger()

        self.configure_bcrypt()

        self.configure_database()

        self.attach_instance()

        self.configure_blueprints()

        self.configure_errorhandler()

        self.configure_jwt()

        self.configure_after_request()

        self.postconfig()

        log.info('Gnar-{} is up'.format(self.display_name))

        run(self.flask, '', self.port)
