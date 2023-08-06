import os
import datetime
import json
import platform
from ctypes import cdll, cast, c_char, c_char_p, c_int, POINTER


class EscherSignerError(Exception):
    pass


filename = None
os_name = platform.system().lower()

if os_name == 'linux':
    filename = 'signer-linux-amd64.so'
elif os_name == 'darwin':
    filename = 'signer-darwin-10.10-amd64.dylib'
else:
    raise EscherSignerError('Platform %s not supported' % os_name)

SO_PATH = os.path.dirname(os.path.abspath(__file__))
GO_SIGNER = cdll.LoadLibrary(os.path.join(SO_PATH, filename))

GO_SIGNER.SignURL.restype = POINTER(c_char)
GO_SIGNER.SignURL.argtypes = [
    POINTER(c_char),
    POINTER(c_char),
    POINTER(c_char),
    POINTER(c_char),
    c_int
]

GO_SIGNER.SignRequest.restype = POINTER(c_char)
GO_SIGNER.SignRequest.argtypes = [
    POINTER(c_char),
    POINTER(c_char),
    POINTER(c_char),
    POINTER(c_char)
]


class EscherSigner:
    def __init__(
            self,
            apiKey,
            apiSecret,
            credentialScope,
            hashAlgo='SHA256',
            algoPrefix='EMS',
            vendorKey='EMS',
            authHeaderName='X-EMS-Auth',
            dateHeaderName='X-EMS-Date'):

        self._config = {
            'accessKeyId': apiKey,
            'apiSecret': apiSecret,
            'hashAlgo': hashAlgo,
            'algoPrefix': algoPrefix,
            'vendorKey': vendorKey,
            'authHeaderName': authHeaderName,
            'dateHeaderName': dateHeaderName,
            'credentialScope': credentialScope
        }

    def signRequest(
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

        raw_result = self._sign_request(
            request, headers_to_sign, date, expires)

        return self._parse_request_sign_result(raw_result)

    def signURL(self, method, url, date=None, expires=600):
        if date is None:
            date = datetime.datetime.utcnow()

        raw_result = self._sign_url(method, url, date, expires)
        return self._parse_url_sign_result(raw_result)

    def _sign_request(self, request, headers_to_sign, date, expires):
        config = self._create_config(date, expires)
        config_json = bytes(json.dumps(config), 'utf-8')

        request_json = bytes(json.dumps(request), 'utf-8')
        headers_to_sign_json = bytes(json.dumps(headers_to_sign), 'utf-8')
        date_str = bytes(date.ctime(), 'utf-8')

        c_result = GO_SIGNER.SignRequest(
            c_char_p(config_json),
            c_char_p(request_json),
            c_char_p(headers_to_sign_json),
            c_char_p(date_str)
        )

        result_json = cast(c_result, c_char_p).value
        return json.loads(result_json.decode('utf-8'))

    def _sign_url(self, method, url, date, expires):
        config = self._create_config(date, expires)
        config_json = bytes(json.dumps(config), 'utf-8')
        method_str = bytes(method, 'utf-8')
        url_str = bytes(url, 'utf-8')
        date_str = bytes(date.ctime(), 'utf-8')

        c_result = GO_SIGNER.SignURL(
            c_char_p(config_json),
            c_char_p(method_str),
            c_char_p(url_str),
            c_char_p(date_str),
            c_int(expires))

        result_json = cast(c_result, c_char_p).value
        return json.loads(result_json.decode('utf-8'))

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
    def _parse_request_sign_result(result):
        if result['SignError'] != '':
            raise EscherSignerError(result['SignError'])

        signed_headers = {}
        for header in result['RequestHeaders']:
            signed_headers[header[0]] = header[1]

        return signed_headers

    @staticmethod
    def _parse_url_sign_result(result):
        if result['SignError'] != '':
            raise EscherSignerError(result['SignError'])

        return result['SignedURL']
