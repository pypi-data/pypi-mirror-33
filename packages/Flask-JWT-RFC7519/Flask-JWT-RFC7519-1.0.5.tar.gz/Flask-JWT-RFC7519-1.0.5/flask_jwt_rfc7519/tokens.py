import datetime
import uuid

from calendar import timegm

import jwt
from werkzeug.security import safe_str_cmp

from flask_jwt_rfc7519.exceptions import JWTDecodeError, CSRFError, \
    IssClaimVerificationError, AudClaimVerificationError
from flask_jwt_rfc7519.config import config


def _create_csrf_token():
    return str(uuid.uuid4())

def _check_claims(default_claims, additional_claims):
    """
    Check that additional claims do no overlap with default claims
    :param default_claims: list with default claims
    :param additional_claims: dictionary with additional claims
    :return: Raise runtime error if overlap
    """
    if additional_claims:
        for claim in default_claims:
            if claim in additional_claims:
                raise RuntimeError("Claim %s in conflict with default claims" % str(claim))

def _encode_jwt(additional_token_data, expires_delta, secret, algorithm,
                json_encoder=None):
    uid = str(uuid.uuid4())
    now = datetime.datetime.utcnow()
    token_data = {
        'iat': now,
        'nbf': now,
        'jti': uid,
    }
    # If expires_delta is False, the JWT should never expire
    # and the 'exp' claim is not set.
    if expires_delta:
        token_data['exp'] = now + expires_delta

    # Make sure additional_token_data is in conflict with default claims
    _check_claims(['iat', 'nbf', 'jti', 'exp'], additional_token_data)
    
    token_data.update(additional_token_data)

    encoded_token = jwt.encode(token_data, secret, algorithm,
                               json_encoder=json_encoder).decode('utf-8')
    return encoded_token


def encode_access_token(identity, secret, algorithm, expires_delta, fresh,
                        additional_claims, csrf, sub_claim_key,
                        json_encoder=None):
    """
    Creates a new encoded (utf-8) access token.

    :param identity: Identifier for who this token is for (ex, username). This
                     data must be json serializable
    :param secret: Secret key to encode the JWT with
    :param algorithm: Which algorithm to encode this JWT with
    :param expires_delta: How far in the future this token should expire
                          (set to False to disable expiration)
    :type expires_delta: datetime.timedelta or False
    :param fresh: If this should be a 'fresh' token or not. If a
                  datetime.timedelta is given this will indicate how long this
                  token will remain fresh.
    :param additional_claims: Custom claims to include in this token. Object
                        must be json serializable
    :param csrf: Whether to include a csrf double submit claim in this token
                 (boolean)
    :param sub_claim_key: Which key should be used to store the identity
    :return: Encoded access token
    """

    if isinstance(fresh, datetime.timedelta):
        now = datetime.datetime.utcnow()
        fresh = timegm((now + fresh).utctimetuple())

    token_data = {
        sub_claim_key: identity,
        'fresh': fresh,
        'type': 'access',
    }

    if config.aud_claim_key:
        token_data['aud'] = config.aud_claim_key
    if config.iss_claim_key:
        token_data['iss'] = config.iss_claim_key

    if csrf:
        token_data['csrf'] = _create_csrf_token()

    # Make sure additional claims is a dict before merge
    if not isinstance(additional_claims, dict):
        raise RuntimeError("Additional claims must be dict")

    if additional_claims:
        # Make sure additional_token_data is in conflict with default claims
        # list(set(l1,l2)) removes duplicates
        _check_claims(list(set(list(token_data.keys()) + ['aud', 'iss', 'csrf'])), additional_claims)
        token_data.update(additional_claims)

    return _encode_jwt(token_data, expires_delta, secret, algorithm,
                       json_encoder=json_encoder)


def encode_refresh_token(identity, secret, algorithm, expires_delta,
                         additional_claims, csrf, sub_claim_key,
                         json_encoder=None):
    """
    Creates a new encoded (utf-8) refresh token.

    :param identity: Some identifier used to identify the owner of this token
    :param secret: Secret key to encode the JWT with
    :param algorithm: Which algorithm to use for the toek
    :param expires_delta: How far in the future this token should expire
                          (set to False to disable expiration)
    :type expires_delta: datetime.timedelta or False
    :param user_claims: Custom claims to include in this token. This data must
                        be json serializable
    :param additional_claims: Custom claims to include in this token. Object
                        must be json serializable
    :param csrf: Whether to include a csrf double submit claim in this token
                 (boolean)
    :param sub_claim_key: Which key should be used to store the identity
    :param user_claims_key: Which key should be used to store the user claims
    :return: Encoded refresh token
    """
    token_data = {
        sub_claim_key: identity,
        'type': 'refresh',
    }

    if config.aud_claim_key:
        token_data['aud'] = config.aud_claim_key
    if config.iss_claim_key:
        token_data['iss'] = config.iss_claim_key

    if csrf:
        token_data['csrf'] = _create_csrf_token()

    # Make sure additional_token_data is in conflict with default claims
    if not isinstance(additional_claims, dict):
        raise RuntimeError("Additional claims must be dict")

    # make sure that additional claims do not contain predefined claims as aud,
    # iss, type, etc.
    # list(set(l1,l2)) removes duplicates
    if additional_claims:
        _check_claims(list(set(list(token_data.keys()) + ['aud', 'iss', 'csrf'])), additional_claims)
        token_data.update(additional_claims)

    return _encode_jwt(token_data, expires_delta, secret, algorithm,
                       json_encoder=json_encoder)


def decode_jwt(encoded_token, secret, algorithm, sub_claim_key, additional_claim_keys, csrf_value=None):
    """
    Decodes an encoded JWT

    :param encoded_token: The encoded JWT string to decode
    :param secret: Secret key used to encode the JWT
    :param algorithm: Algorithm used to encode the JWT
    :param sub_claim_key: expected key that contains the identity
    :param additional_claim_keys: expected key that contains the additional claims
    :param csrf_value: Expected double submit csrf value
    :param type: The type of token to decode (access or refresh)
    :return: Dictionary containing contents of the JWT
    """
    # This call verifies the ext, iat, and nbf claims
    audience = None
    if config.aud_claim_key:
        audience = config.aud_claim_key
    issuer = None
    if config.iss_claim_key:
        issuer = config.iss_claim_key

    options = dict(require_iat=True,require_nbf=True)

    try:
        data = jwt.decode(encoded_token, secret, algorithms=[algorithm], options=options, audience=audience, issuer=issuer)

    # aud claim not valid
    except jwt.InvalidAudienceError:
        raise AudClaimVerificationError
    # iss claim not valid
    except jwt.InvalidIssuerError:
        raise IssClaimVerificationError
    except jwt.MissingRequiredClaimError as e:
        raise JWTDecodeError(e)
    except jwt.DecodeError as e:
        raise JWTDecodeError(e)

    # Make sure that any custom claims we expect in the token are present
    if 'jti' not in data:
        raise JWTDecodeError("Missing claim: jti")
    if sub_claim_key not in data:
        raise JWTDecodeError("Missing claim: {}".format(sub_claim_key))
    if 'type' not in data or data['type'] not in ('refresh', 'access'):
        raise JWTDecodeError("Missing or invalid claim: type")
    if data['type'] == 'access':
        if 'fresh' not in data:
            raise JWTDecodeError("Missing claim: fresh")

    if data['type'] != 'refresh' or config.claims_in_refresh_token:
        for claim in additional_claim_keys:
            if claim not in data:
                raise JWTDecodeError("Missing claim %s" % str(claim))

    if csrf_value:
        if 'csrf' not in data:
            raise JWTDecodeError("Missing claim: csrf")
        if not safe_str_cmp(data['csrf'], csrf_value):
            raise CSRFError("CSRF double submit tokens do not match")
    return data
