
import requests

try:
    from urllib.parse import urljoin
except ImportError:
    from urlparse import urljoin

from copy import deepcopy

API_ROOT = 'https://www.alphanym.com/api/v0/'

class AlphanymException(Exception):
    def __init__(self, data):
        self._data = data

    def data(self):
        return deepcopy(self._data)

def query(token, name, email=None):
    """
    Query the Alphanym API, to parse anyone's name into semantically significant parts.
    """

    url = _alphanym_url('english/query/')

    body = _get_request_body(
        token=token,
        name=name,
        email=email,
    )

    return _alphanym_request(url, body)

def feedback(token, name, email=None, alphanym=None, betanym=None, version=None):
    """
    Correct a mistake Alphanym made when attempting to interpret a name.
    """

    url = _alphanym_url('english/feedback/')

    body = _get_request_body(
        token=token,
        name=name,
        email=email,
        alphanym=alphanym,
        betanym=betanym,
        version=version,
    )

    return _alphanym_request(url, body)

def _get_request_body(token, name, **kw):
    body = {}

    if isinstance(name, str):
        body.update(**kw)
        body.update(**{
            'token': token,
            'name': name,
        })
    else:
        # Name is dict like.
        body.update(**name)
        body.update(**{
            'token': token,
        })

    return body

def _alphanym_url(path):
    return urljoin(
        API_ROOT,
        path,
    )

def _alphanym_request(url, body):
    try:
        response = requests.post(
            url,
            json=body,
        )
    except requests.RequestException as exc:
        raise AlphanymException(exc.response.json())
    else:
        if str(response.status_code).startswith('2'):
            return response.json()
        else:
            raise AlphanymException(response.json())
