import json
from werkzeug.exceptions import BadRequest
from lp_rest_kernel.rest import EnterpriseRestApi
from lp_api_kernel.exceptions import ItemNotFoundException
from flask import url_for
from logging import CRITICAL, ERROR, WARNING, INFO, DEBUG, getLogger

##
# Inspired by https://github.com/PACKED-vzw/scoremodel/blob/master/scoremodel/modules/api/rest/scoremodel.py
# (c) Pieter De Praetere, PACKED vzw - 2016 - GPLv2
# (c) Infrabel Linux Team - 2017-2018 - GPLv2
##


class EnterpriseRestWrapperApi:
    ##
    # This table translates between API methods
    # and api_class methods. Useful when you want
    # to use another function to perform a .read().
    translation_table = {
        'post': 'create',
        'get': 'read',
        'put': 'update',
        'delete': 'delete',
        'list': 'list'
    }

    def __init__(self, api_class, o_request, api_obj_id=None, hooks=(), translate=None, prehooks=(), posthooks=(),
                 debug=False, pass_args=False, response_data_raw=False, **kwargs):
        """
        This class is an REST API class that translates between request methods and
        methods of the api_class class.
        It performs the following functions:
            - Translate between request.method and self.action()
                GET => self.get(api_obj_id) | self.list() if api_obj_id is None
                DELETE => self.delete(api_obj_id)
                POST => self.post(o_request.get_data().decode())
                PUT => self.put(api_obj_id, o_request.get_data().decode())
            - Translate between self.action() and api_class.action() using translate or self.translation_table
                if translate is None.
            - Performs functions in hooks on the decoded but unparsed data from the original request.
                All functions take input_data_string as input and must return it (after they applied their actions).
                The order of the hooks can not be guaranteed.
            - Converts the request data to JSON.
            - Takes the reply from api_class (in JSON) and convert it to a response with the correct
                status code and headers.
            - On error: generate an error message, error code and error status code.
        :param api_class:
        :param o_request:
        :param api_obj_id:
        :param hooks:
        :param translate:
        :param additional_opts:
        :param prehooks:
        :param posthooks:
        :param debug:
        :param pass_args:
        :param response_data_raw: do not wrap the response in a {data:, msg:} object
        """
        self.logger = getLogger('flask.app')
        if pass_args:
            self.api = api_class(**kwargs)
        else:
            self.api = api_class()
        self.request = o_request
        self.msg = None
        self.output_data = u''
        self.status_code = 200
        self.debug = debug
        self.headers = {}
        self.response_data_raw = response_data_raw

        if translate is None:
            self.translate = self.translated_functions(self.translation_table)
        else:
            self.translate = self.translated_functions(translate)

        if len(prehooks) == 0 and len(hooks) > 0:
            prehooks = hooks
        ##
        # Normally we would use .get_data() and convert the bytes to a string
        # but CsrfProtect() already parses the form, thus emptying .get_data()
        # We use this trick so all other functions remain unchanged.
        # Note that we still have to implement some kind of error reporting when
        # the automatic parsing fails.
        ##
        input_data_json = {}
        if self.request.method != 'GET' and self.request.method != 'DELETE':
            try:
                input_data_json = self.request.get_json(force=True, silent=False)
            except BadRequest as e:
                self.msg = str(e)
                self.status_code = 400
                self.log(e)
                if self.debug:
                    raise e
        if self.status_code != 400:
            try:
                for hook in prehooks:
                    input_data_json = hook(input_data_json)
            except Exception as e:
                self.msg = str(e)
                self.status_code = 400
                self.log(e)
                if self.debug:
                    raise e
            else:
                try:
                    self.parse_request(input_data_json=input_data_json, api_obj_id=api_obj_id, **kwargs)
                except ItemNotFoundException as e:
                    self.msg = str(e)
                    self.log(e)
                    self.status_code = 404
        ##
        # Set self.response
        ##
        if not self.status_code or self.status_code < 400:
            if len(posthooks) > 0:
                try:
                    for hook in posthooks:
                        self.output_data = hook(self.output_data, self.update_status_code)
                except Exception as e:
                    self.msg = str(e)
                    self.status_code = 400
                    self.log(e)
                    if self.debug:
                        raise e
        if not self.status_code:
            self.status_code = 200
        self.response = self.create_response(self.output_data)

    def post(self, input_data, **kwargs):
        try:
            created_object = self.translate['post'](input_data=input_data, **kwargs)
        except Exception as e:
            self.msg = str(e)
            self.status_code = 400
            created_object = None
            self.log(e)
            if self.debug:
                raise e
        else:
            self.msg = '{0}: {1} created.'.format(self.api, created_object)
        if created_object is not None:
            return self.get_output(created_object)
        else:
            return u''

    def get(self, item_id, **kwargs):
        try:
            found_object = self.translate['get'](item_id, **kwargs)
        except Exception as e:
            self.msg = str(e)
            self.status_code = 400
            found_object = None
            self.log(e)
            if self.debug:
                raise e
        else:
            self.msg = '{0}: {1} found.'.format(self.api, item_id)
        if found_object is not None:
            return self.get_output(found_object)
        else:
            return u''

    def list(self, **kwargs):
        try:
            found_objects = self.api.list(**kwargs)
        except Exception as e:
            self.msg = str(e)
            self.status_code = 400
            found_objects = None
            self.log(e)
            if self.debug:
                raise e
        if found_objects is not None:
            self.msg = '{0} found.'.format(self.api)
            if isinstance(found_objects, list):
                out_results = []
                for found_object in found_objects:
                    out_results.append(self.get_output(found_object))
            else:
                out_results = self.get_output(found_objects)
            return out_results
        else:
            return u''

    def put(self, item_id, input_data, **kwargs):
        try:
            updated_object = self.api.update(item_id, input_data=input_data, **kwargs)
        except Exception as e:
            self.msg = str(e)
            self.status_code = 400
            updated_object = None
            self.log(e)
            if self.debug:
                raise e
        else:
            self.msg = '{0}: {1} updated.'.format(self.api, updated_object)
        if updated_object is not None:
            return self.get_output(updated_object)
        else:
            return u''

    def delete(self, item_id, **kwargs):
        try:
            deleted_object = self.api.delete(item_id, **kwargs)
        except Exception as e:
            self.msg = str(e)
            self.status_code = 400
            deleted_object = False
            self.log(e)
            if self.debug:
                raise e
        else:
            self.msg = '{0}: {1} deleted.'.format(self.api, item_id)
        if deleted_object is True:
            return u''
        else:
            return u''

    def parse_get(self, api_obj_id=None, **kwargs):
        """
        Parse a GET request
        :param api_obj_id:
        :return:
        """
        if api_obj_id is None:
            if hasattr(self.api, 'list'):
                self.output_data = self.list(**kwargs)
            else:
                self.msg = 'Parameter {0} missing.'.format('api_obj_id')
                self.status_code = 400
                self.log(self.msg)
        else:
            self.output_data = self.get(api_obj_id, **kwargs)

    def parse_delete(self, api_obj_id=None, **kwargs):
        """
        Parse a DELETE request
        :param api_obj_id:
        :return:
        """
        if api_obj_id is None:
            self.msg = 'Parameter {0} missing.'.format('api_obj_id')
            self.status_code = 400
            self.log(self.msg)
        else:
            self.output_data = self.delete(api_obj_id, **kwargs)

    def parse_put(self, api_obj_id=None, input_data_json=None, **kwargs):
        """
        Parse a PUT request
        :param api_obj_id:
        :param input_data_json:
        :return:
        """
        if api_obj_id is None:
            self.msg = 'Parameter {0} missing.'.format('api_obj_id')
            self.status_code = 400
            self.log(self.msg)
        else:
            if input_data_json is not None:
                self.output_data = self.put(api_obj_id, input_data_json, **kwargs)
            else:
                self.msg = 'Parameter {0} missing.'.format('body')
                self.status_code = 400
                self.log(self.msg)

    def parse_post(self, input_data_json, **kwargs):
        """
        Parse a POST request
        :param input_data_json:
        :return:
        """
        if input_data_json is not None:
            self.output_data = self.post(input_data_json, **kwargs)
        else:
            self.msg = 'Parameter {0} missing.'.format('body')
            self.status_code = 400
            self.log(self.msg)

    def parse_request(self, **kwargs):
        """
        Parse the original request:
            - Check for missing arguments and input
            - Execute self.action() for the request.method (self.request)
        This function has many sub functions (parse_*) to allow for easier
        subclassing.
        :return:
        """
        if self.request.method == 'GET':
            self.parse_get(**kwargs)
        elif self.request.method == 'DELETE':
            self.parse_delete(**kwargs)
        elif self.request.method == 'PUT':
            self.parse_put(**kwargs)
        elif self.request.method == 'POST':
            self.parse_post(**kwargs)
        else:
            self.msg = 'Illegal action requested: {0}.'.format(self.request.method)
            self.status_code = 405
            self.log(self.msg)

    def create_response(self, data):
        """
        Create an API response
        :param data:
        :return:
        """
        rest_api = EnterpriseRestApi()
        return rest_api.response(status=self.status_code, data=data, msg=self.msg, headers=self.headers,
                                 raw=self.response_data_raw)

    def parse_json(self, unparsed_string):
        try:
            parsed_string = json.loads(unparsed_string)
        except ValueError as e:
            self.msg = u'A JSON error occurred: {0}'.format(e)
            self.log(e)
            if self.debug:
                raise e
            return None
        return parsed_string

    def translated_functions(self, translation_table):
        """
        Take translation_table and self.api: return the function with that name in such a way
        that it can be called (https://stackoverflow.com/questions/3061/calling-a-function-of-a-module-from-a-string-with-the-functions-name-in-python)
        :return:
        """
        translation = {}
        for our_function, api_function in translation_table.items():
            call_function = getattr(self.api, api_function)
            translation[our_function] = call_function
        return translation

    def get_output(self, obj):
        if hasattr(obj, 'output_obj'):
            return obj.output_obj()
        else:
            if hasattr(obj, 'ready'):
                return {
                    'task_id': obj
                }
            return obj

    def get_task_id(self):
        task_id = self.request.args.get('status')
        if task_id and task_id != '':
            return task_id
        return None

    def update_status_code(self, status_code):
        self.status_code = status_code

    def log(self, msg, level=ERROR):
        message = '{0}: {1}'.format(self.request.full_path, msg)
        self.logger.log(level, message)
