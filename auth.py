from datetime import datetime
from functools import wraps

import jwt
from flask import request
from werkzeug.exceptions import Forbidden


def _get_claims(audience, ttl):
    from server import app
    return {
        # Expiration Time Claim
        'exp': datetime.utcnow() + ttl,
        # Not Before Time Claim
        'nbf': datetime.utcnow(),
        # Issuer Claim
        'iss': app.config['ISSUER'],
        # Audience Claim
        'aud': audience,
        # Issued At Claim
        'iat': datetime.utcnow()
    }


def sign_start_registration(data):
    from server import app
    payload = {**data, **_get_claims(app.config['REGISTRATION_AUDIENCE'],
                                     app.config['REGISTRATION_TOKEN_LIFE_TIME'])}
    return jwt.encode(payload, app.config['HMAC_KEY'],
                      algorithm=app.config['REGISTRATION_ALGORITHM'])


def sign_challenge(data):
    from server import app
    payload = {**data, **_get_claims(app.config['CHALLENGE_AUDIENCE'],
                                     app.config['CHALLENGE_TOKEN_LIFE_TIME'])}
    return jwt.encode(payload, app.config['HMAC_KEY'], algorithm=app.config['CHALLENGE_ALGORITHM'])


def sign_login_credentials(data):
    from server import app
    payload = {**data,
               **_get_claims(app.config['MS2_AUDIENCE'], app.config["LOGIN_TOKEN_LIFE_TIME"])}
    return jwt.encode(payload, app.config['PRIVATE_ECDSA_KEY'],
                      algorithm=app.config['LOGIN_ALGORITHM'])


def verify_registration_started(token):
    from server import app
    return jwt.decode(token, app.config['HMAC_KEY'],
                      audience=app.config['REGISTRATION_AUDIENCE'],
                      issuer=app.config['ISSUER'],
                      algorithms=app.config['REGISTRATION_ALGORITHM'])


def verify_logged_in(token):
    from server import app
    return jwt.decode(token, app.config['PUBLIC_ECDSA_KEY'],
                      audience=app.config['MS2_AUDIENCE'],
                      issuer=app.config['ISSUER'],
                      algorithms=app.config['LOGIN_ALGORITHM'])


def verify_challenged(token):
    from server import app
    return jwt.decode(token, app.config['HMAC_KEY'],
                      audience=app.config['CHALLENGE_AUDIENCE'],
                      issuer=app.config['ISSUER'],
                      algorithms=app.config['CHALLENGE_ALGORITHM'])


def verify_jwt(check=None):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            auth_type, auth_value = auth_header.split()
            if auth_type != "JWT":
                return Forbidden("JWT required")
            auth_data = check(auth_value)
            request.authorization = auth_data
            return f(*args, **kwargs)

        return wrapped

    return decorator
