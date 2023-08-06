# Flask-PubSubDecorator

Decorates publisher functions and subscriber routes creating topics/subscriptions if necessary.

## Installation

Add this line to your application's requirements.txt

```python
Flask-PubSubDecorator
```

And then execute:

    $ pip install -r requirements.txt

Or install it yourself as:

    $ pip install Flask-PubSubDecorator

## Usage

Using PubSubDecorator is dead simple. First set your GOOGLE_APPLICATION_CREDENTIALS environment variable to point at a valid JSON creds file.

    $ export GOOGLE_APPLICATION_CREDENTIALS=/path/to/creds.json

The following snippet should get you coding
```python
from flask import Flask, request
from PubSubDecorator import PubSubDecorator
import base64
import json


app = Flask(__name__)
# blueprint can optionally be passed in for registering subscribers in a blueprint endpoint
app.pubsub = PubSubDecorator(app)


# publisher decorator will inject publisher client and topic path
@app.pubsub.publisher(topic='user_confirmed')
def user_confirmed(publisher, topic, user):
    publisher.publish(topic, data=json.dumps({
        'user_id': user.id
    }))


# subscriber decorator will register the Flask route, prefixing /_ah/push-handlers
# subscriber decorator will parse and inject pubsub message
@app.pubsub.subscriber(
    subscription='process_user_confirmation',
    topic='user_confirmed',
    route='/process_user_confirmation',
    methods=['POST']
)
def process_user_confirmation(message, *args, **kwargs):
    try:
        user_id = message.get('user_id')
        # do some async work here!
    except Exception:
        _logger.exception(
            'An unexpected error occurred processing subscription "{0}": {1}'.format(
                kwargs.get('__subscription__'), request.data
            )
        )
        # Unexpected failure, do not ack message
        return '', 422
    return '', 200
```

## Security

PubSub push subscriptions are inherently public facing and should therefore be secured. Googles recommended solution
is to attach a secret key to a registered subscription pushEndpoint. PubSubDecorator handles this for you if any of
the following is provided:

  1. OS Environment Variable `PUBSUB_DECORATOR_API_KEY`
  2. Flask App Config `PUBSUB_DECORATOR_API_KEY`
  3. api_key is passed into PubSubDecorator constructor.

Best Practice: encrypt your key with GCloud KMS, store it in GCloud Datastore, and export to OS environment variable
at runtime.

## Logging

Decorators will log to 'flask-pubsub-decorator' namespace.

```python
import sys
import logging
import logging.handlers


logger = logging.getLogger('flask-pubsub-decorator')
logger.setLevel(logging.DEBUG)
log_file = logging.handlers.RotatingFileHandler(
    'log_file_name.log', maxBytes=5 * 1024 * 1024, backupCount=10
)
logger.addHandler(log_file)
```

# Testing

    $ pytest -s tests.py
