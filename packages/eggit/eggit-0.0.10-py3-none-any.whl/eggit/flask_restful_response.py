from flask import json, make_response

from .sqlalchemy_adapter import sqlalchemy_encoder


class JsonResult():
    def __init__(self, msg, bool_status, data, error_code):
        self._msg = msg
        self._bool_status = bool_status
        self._data = data
        self._error_code = error_code

    def get_dict(self):
        result = dict(bool_status=self._bool_status)
        if self._msg:
            result['msg'] = self._msg

        if self._data:
            result['data'] = self._data

        if self._error_code:
            result['error_code'] = self._error_code

        return result


def response(msg=None,
             bool_status=False,
             data=None,
             error_code=None,
             data_encoder=True,
             content_type=None):

    content = JsonResult(msg, bool_status, data, error_code)

    result = make_response(
        json.dumps(
            content.get_dict(),
            cls=(sqlalchemy_encoder() if data_encoder else None),
            check_circular=False,
            ensure_ascii=False))

    if content_type:
        result.headers['Content-Type'] = content_type

    return result


def ok(data=None, msg='ok', data_encoder=True, content_type='application/json;charset=UTF-8'):
    return response(msg, True, data, None, data_encoder, content_type)


def error(data=None, msg='error', error_code=None, content_type='application/json;charset=UTF-8'):
    return response(msg, False, data, error_code, content_type=content_type)


def blank(data=None, msg='no content', error_code=None, content_type='application/json;charset=UTF-8'):
    return response(msg, False, data, error_code, content_type=content_type)
