'''
@author: Dimitrios Kanellopoulos
@contact: jimmykane9@gmail.com
'''
import os
import logging

class JSONHandler():

    '''
        msg(optional): A str with a message
        status_code(optional): The following subset of HTTP codes
            200(default): Success on operation.
            400: Bad Request. Something missing in the post or get params?
            401: Unauthorized. Use it for user authorization problems.
            403: Forbidden. Use it for logical unaccepted operations.
            404: Not found. Use it if the model is not found.
            500: Internal Server Error. If you can catch an exception.

    '''
    def get_status (self, status_code=200, msg=None):

        # Put more here if needed
        statuses = [
            {'code': 200, 'message': 'Success', 'info': msg},
            {'code': 400, 'message': 'Bad Request. Parameters are invalid', 'info': msg},
            {'code': 401, 'message': 'Unauthorized. You don\'t have permission to touch this', 'info': msg},
            {'code': 403, 'message': 'Forbidden. Sorry my AI does not allow me to do that.', 'info': msg},
            {'code': 404, 'message': 'Not found. The object was not found', 'info': msg},
            {'code': 500, 'message': 'Internal Server Error', 'info': msg},
        ]

        status = [ status for status in statuses if status['code'] == status_code][0]
        return status

    # This should be moved elsewhere
    def is_dev_server(self):
        return os.environ['SERVER_SOFTWARE'].startswith('Dev')


    def remove_html_markup(input):

        tag = False
        quote = False
        out = ""

        for c in input:
            if c == '<' and not quote:
                tag = True
            elif c == '>' and not quote:
                tag = False
            elif (c == '"' or c == "'") and tag:
                quote = not quote
            elif not tag:
                out = out + c
        return out