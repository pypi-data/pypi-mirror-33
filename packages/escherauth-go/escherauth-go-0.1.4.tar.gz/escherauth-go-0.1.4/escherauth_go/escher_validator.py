import os
import datetime
import json
import platform
from urllib.parse import urlsplit, urlunsplit
from ctypes import cdll, cast, c_char_p, c_char, POINTER


class EscherValidatorError(Exception):
    pass


filename = None
os_name = platform.system().lower()

if os_name == 'linux':
    filename = 'validator-linux-amd64.so'
elif os_name == 'darwin':
    filename = 'validator-darwin-10.10-amd64.dylib'
else:
    raise EscherValidatorError('Platform %s not supported' % os_name)


SO_PATH = os.path.dirname(os.path.abspath(__file__))
LIB = cdll.LoadLibrary(os.path.join(SO_PATH, filename))
LIB.ValidateRequest.restype = POINTER(c_char)
LIB.ValidateRequest.argtypes = [
    POINTER(c_char),
    POINTER(c_char),
    POINTER(c_char),
    POINTER(c_char),
    POINTER(c_char)
]


class EscherValidator:
    def __init__(
            self,
            credentialScope,
            keyDB,
            hashAlgo='SHA256',
            algoPrefix='EMS',
            vendorKey='EMS',
            authHeaderName='X-EMS-Auth',
            dateHeaderName='X-EMS-Date'):

        self._config = {
            'hashAlgo': hashAlgo,
            'algoPrefix': algoPrefix,
            'vendorKey': vendorKey,
            'authHeaderName': authHeaderName,
            'dateHeaderName': dateHeaderName,
            'credentialScope': credentialScope
        }

        self._keyDB = keyDB

    def validateRequest(
            self,
            method,
            url,
            body,
            headers,
            headers_to_sign=None,
            date=None,
            expires=600):
        if date is None:
            date = datetime.datetime.utcnow()

        if headers_to_sign is None:
            headers_to_sign = []

        request = self._create_request(method, url, headers, body)

        raw_result = self._validate_request(
            request, headers_to_sign, date, expires)

        return raw_result

    def validateURL(
            self,
            method,
            url,
            headers=None,
            headers_to_sign=None,
            date=None,
            expires=600):

        if headers is None:
            headers = {}

        if 'Host' not in headers and 'host' not in headers:
            parsed_url = urlsplit(url)
            url_to_check = urlunsplit([
                '', '', parsed_url[2], parsed_url[3], parsed_url[4]
            ])
            headers['Host'] = parsed_url[1]

        return self.validateRequest(
            method,
            url_to_check,
            '',
            headers,
            headers_to_sign,
            date,
            expires)

    def _validate_request(self, request, headers_to_sign, date, expires):
        config = self._create_config(date, expires)
        config_json = bytes(json.dumps(config), 'utf-8')

        request_json = bytes(json.dumps(request), 'utf-8')
        keydb_json = bytes(json.dumps(self._keyDB), 'utf-8')
        headers_to_sign_json = bytes(json.dumps(headers_to_sign), 'utf-8')
        date_str = bytes(date.ctime(), 'utf-8')

        c_result = LIB.ValidateRequest(
            c_char_p(config_json),
            c_char_p(request_json),
            c_char_p(keydb_json),
            c_char_p(headers_to_sign_json),
            c_char_p(date_str)
        )

        c_result = cast(c_result, c_char_p).value
        raw_result = json.loads(c_result.decode('utf-8'))
        return self._parse_validation_result(raw_result)

    def _create_config(self, date, expires):
        config = self._config.copy()
        config['date'] = date.ctime()
        config['expires'] = expires
        return config

    @staticmethod
    def _create_request(method, url, headers, body):
        headers_dict = [[key, val] for (key, val) in headers.items()]
        return {
            'method': method,
            'url': url,
            'headers': headers_dict,
            'body': body
        }

    @staticmethod
    def _parse_validation_result(result):
        if result['ValidationError'] != '':
            raise EscherValidatorError(result['ValidationError'])

        return result['KeyID']
