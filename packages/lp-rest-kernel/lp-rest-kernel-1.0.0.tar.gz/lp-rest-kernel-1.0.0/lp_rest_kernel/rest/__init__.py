from flask import make_response
import json


class EnterpriseRestApi:

    def __init__(self):
        self.__response = make_response()

    def response(self, status=None, data=None, msg=None, headers=None, raw=False):
        if raw:
            self.__response.data = json.dumps(data, default=lambda o: str(o))
        else:
            self.__response.data = json.dumps({
                'msg': msg,
                'data': data
            }, default=lambda o: str(o))
        self.__response.status_code = 200
        if status:
            self.__response.status_code = status

        self.headers()
        if headers:
            for key, value in headers.items():
                self.__response.headers[key] = value
        return self.__response

    def headers(self):
        self.__response.headers['Content-Type'] = 'application/json'
        self.__response.headers['Access-Control-Allow-Origin'] = '*'
