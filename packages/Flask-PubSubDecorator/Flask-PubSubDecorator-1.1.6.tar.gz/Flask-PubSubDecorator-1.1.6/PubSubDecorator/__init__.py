from clint.textui import colored
from flask import Flask, Blueprint, request, make_response, wrappers
from google.cloud import pubsub_v1
import google.auth
from google.auth.transport.requests import AuthorizedSession
from requests.exceptions import HTTPError
import logging
import json
import base64
import os
import commands
import click
import sys
from gcredstash import GoogleKMS, KeyStore
import googleapiclient.discovery
try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode

_publisher = pubsub_v1.PublisherClient()
_subscriber = pubsub_v1.SubscriberClient()
_logger = logging.getLogger('flask-pubsub-decorator')
_publish_cli_commands = ['debug', 'shell_plus', 'run', 'run_production']
_subscribe_cli_commands = ['debug', 'run', 'run_production']


class PubSubDecorator(object):
    _kms = None

    def __init__(
        self, app, blueprint=None, publish_cli_commands=_publish_cli_commands,
        subscribe_cli_commands=_subscribe_cli_commands, api_key=None
    ):
        if not isinstance(app, Flask):
            raise ValueError('PubSubDecorator must be initialized with a Flask app')
        if blueprint and not isinstance(blueprint, Blueprint):
            raise ValueError('PubSubDecorator blueprint param must be Flask Blueprint')

        scopes = [
            'https://www.googleapis.com/auth/pubsub'
        ]

        self.app = app
        self.api_key = (
            api_key or app.config.get('PUBSUB_DECORATOR_API_KEY') or os.environ.get('PUBSUB_DECORATOR_API_KEY')
        )
        self.blueprint = blueprint
        self.pub_client = _publisher
        self.sub_client = _subscriber
        self.creds, self.project_id = google.auth.default(scopes)
        self.env = os.environ.get(app.config.get('APP_ENV_VAR'))
        self.publishable = True
        self.subscriptable = True

        if not self.creds:
            raise ValueError('Failed to establish google.auth.credentials.Credentials')

        if not os.environ.get('GAE_DEPLOYMENT_ID'):
            if (
                self.env is not None and not commands.getoutput('gcloud config get-value project').endswith(self.env)
                or self.env is not None and not os.environ.get('GCLOUD_PROJECT', '').endswith(self.env)
                or '--no-pubsub' in sys.argv or sys.argv == [''] or bool(os.environ.get('PUBSUB_DECORATOR_DISABLE'))
            ):
                self.publishable = False
                self.subscriptable = False
                return
        try:
            click_ctx = click.get_current_context()
            if click_ctx:
                click_ctx.resilient_parsing = True
                cli_command = (app.cli.parse_args(click_ctx, sys.argv) or [''])[0]
                self.publishable = cli_command in publish_cli_commands
                self.subscriptable = cli_command in subscribe_cli_commands
        except RuntimeError:
            self.publishable = True
            self.subscriptable = True

    def _get_future_key(self):
        if not self._kms:
            self._kms = GoogleKMS(
                googleapiclient.discovery.build('cloudkms', 'v1'),
                os.environ.get('GCREDSTASH_GCP_PROJECT_ID'),
                os.environ.get('GCREDSTASH_DEFAULT_LOCATION_ID'),
                os.environ.get('GCREDSTASH_DEFAULT_KEY_RING_ID'),
                KeyStore(os.environ.get('GCREDSTASH_GCP_PROJECT_ID'))
            )

        return self._kms.get(
            os.environ.get('GCREDSTASH_DEFAULT_KEY_RING_ID'),
            os.environ.get('GCREDSTASH_DEFAULT_DATASTORE_KIND'),
            'PUBSUB_DECORATOR_API_KEY',
        )

    def _get_authed_session(self):
        return AuthorizedSession(self.creds)

    def _make_request(self, method, url, data=None, headers=None, **kwargs):
        authed_session = self._get_authed_session()
        method = method.upper()

        if 'params' in kwargs:
            _logger.info(u'{method} Request: {url}?{query}'.format(
                method=method, url=url, query=urlencode(kwargs['params']))
            )
        else:
            _logger.info(u'{method} Request: {url}'.format(method=method, url=url))
        if 'json' in kwargs:
            _logger.info('PAYLOAD: {json}'.format(**kwargs))
        if headers:
            _logger.info('HEADERS: {0}'.format(headers))

        r = authed_session.request(method, url, data, headers, **kwargs)

        _logger.info(
            u'{method} Response: {status} {text}'.format(
                method=method, status=r.status_code, text=r.text
            )
        )

        return r

    def _build_topic_or_subscription_env_var(self, topic_or_subscription):
        return 'PUBSUB_{0}'.format(topic_or_subscription.replace('/', '_').replace('-', '_').upper())

    def should_create_topic(self, topic):
        if not self.publishable:
            return False
        else:
            return not bool(os.environ.get(self._build_topic_or_subscription_env_var(topic)))

    def should_create_subscription(self, subscription):
        if not self.subscriptable:
            return False
        else:
            return not bool(os.environ.get(self._build_topic_or_subscription_env_var(subscription)))

    def publisher(self, topic):
        if not topic:
            raise ValueError('You must specify a topic when using publisher decorator')

        topic = self.pub_client.topic_path(self.project_id, topic)

        def decorator(f):
            def wrap_f(*args, **kwargs):
                return f(self.pub_client, topic, *args, **kwargs)
            return wrap_f

        if not self.should_create_topic(topic):
            return decorator
        else:
            print colored.yellow('Establishing PubSub topic {0}'.format(topic))

            try:
                r = self._make_request('GET', 'https://pubsub.googleapis.com/v1/' + topic)
                r.raise_for_status()
            except HTTPError:
                _logger.info(colored.yellow('Decorating Topic: {0}'.format(topic)))
                r = self._make_request('PUT', 'https://pubsub.googleapis.com/v1/' + topic)
                r.raise_for_status()

            os.environ[self._build_topic_or_subscription_env_var(topic)] = '1'

            return decorator

    def subscriber(self, subscription, topic, route=None, methods=None, push=True):
        if not subscription:
            raise ValueError('You must specify a subscription when using subscriber decorator')
        if not topic:
            raise ValueError('You must specify a topic when using subscriber decorator')
        if push:
            if not route:
                raise ValueError('You must specify a route when using subscriber decorator')
            if not methods:
                methods = ['POST']

        # stupid python https://www.python.org/dev/peps/pep-3104/
        decorator_args = (subscription, topic, route, methods, push)

        def decorator(f):
            subscription, topic, route, methods, push = decorator_args
            self.publisher(topic)
            subscription = self.sub_client.subscription_path(self.project_id, subscription)
            topic = self.sub_client.topic_path(self.project_id, topic)

            if push:
                if self.blueprint:
                    route = self.blueprint.url_prefix + route

                route = '/_ah/push-handlers' + route

            push_endpoint = self.app.config.get('APPSPOT_URL')
            if not push_endpoint:
                push_endpoint = 'https://{0}.appspot.com'.format(self.project_id)

            push_endpoint += route

            if self.env == 'dev' or not push:
                push_config = {}
            elif self.api_key:
                push_config = {
                    'pushEndpoint': '{0}/{1}'.format(push_endpoint, self.api_key)
                }
                route += '/<pubsub_decorator_api_key>'
            else:
                push_config = {
                    'pushEndpoint': push_endpoint
                }

            if self.should_create_subscription(subscription):
                print colored.green('Establishing PubSub {0} subscription {1}'.format(
                    'pull' if self.env == 'dev' or not push else 'push', subscription
                ))

                try:
                    r = self._make_request('POST', 'https://pubsub.googleapis.com/v1/{0}:modifyPushConfig'.format(
                        subscription
                    ), json={
                        'pushConfig': push_config
                    })
                    r.raise_for_status()
                except HTTPError:
                    _logger.info(colored.yellow('Decorating Subscription: {0}'.format(subscription)))
                    r = self._make_request('PUT', 'https://pubsub.googleapis.com/v1/' + subscription, json={
                        'ackDeadlineSeconds': 600,
                        'pushConfig': push_config,
                        'topic': topic
                    })
                    r.raise_for_status()

                os.environ[self._build_topic_or_subscription_env_var(subscription)] = '1'

            push_endpoint = push_config.get('pushEndpoint')

            if self.blueprint:
                endpoint = '{0}.{1}'.format(self.blueprint.name, f.func_name)
            else:
                endpoint = f.func_name

            def dev_f(message, *args, **kwargs):
                kwargs.update({
                    '__publisher__': self.pub_client,
                    '__topic__': topic,
                    '__subscriber__': self.sub_client,
                    '__subscription__': subscription,
                    '__push_endpoint__': push_endpoint
                })

                try:
                    r = f(json.loads(message.data), *args, **kwargs)
                    # if func returns result, it should be a flask route response.
                    # ack message if successful response, or no response with no exception
                    if r:
                        if not isinstance(r, wrappers.Response):
                            with self.app.app_context():
                                r = make_response(r)
                        if r.status_code < 400:
                            message.ack()
                    else:
                        message.ack()
                except Exception:
                    _logger.exception('Failed to process dev subscription "{0}" Message: {1}'.format(
                        subscription, message.data
                    ))

            def wrap_f(*args, **kwargs):
                message = {}

                if request:
                    try:
                        envelope = json.loads(request.data.decode('utf-8'))
                        message = json.loads(base64.b64decode(envelope['message']['data']))
                        _logger.info('{0} Envelope: {1}'.format(subscription, envelope))
                    except Exception:
                        _logger.exception(
                            'Failed to parse subscription "{0}" Envelope: {1}'.format(subscription, request.data)
                        )

                    if self.api_key and kwargs.get('pubsub_decorator_api_key') != self.api_key:
                        if kwargs.get('pubsub_decorator_api_key') == self._get_future_key():
                            logger = _logger.info
                            status_code = 409
                        else:
                            logger = _logger.error
                            status_code = 403

                        logger(
                            'Invalid Request (Wrong API KEY) against PubSub Subscription "{0}".\n'
                            'API Key "{1}" != "{2}"\n'
                            'DATA: {3}'
                            .format(subscription, kwargs.get('pubsub_decorator_api_key'), self.api_key, request.data)
                        )
                        return '', status_code

                kwargs.update({
                    '__publisher__': self.pub_client,
                    '__topic__': topic,
                    '__subscriber__': self.sub_client,
                    '__subscription__': subscription,
                    '__push_endpoint__': push_endpoint
                })

                return f(message, *args, **kwargs)

            if push:
                self.app.route(route, endpoint=endpoint, methods=methods)(wrap_f)
            if (self.env == 'dev' or not push) and self.subscriptable:
                self.sub_client.subscribe(subscription, callback=dev_f)
            return wrap_f
        return decorator
