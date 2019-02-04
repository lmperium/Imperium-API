"""
{
    "error": "error description",
    "message": "error message"
}
"""

from flask import jsonify
from werkzeug.http import HTTP_STATUS_CODES


def error_response(status_code, message=None):
    body = {
        'error': HTTP_STATUS_CODES.get(status_code),
    }

    if message:
        body['message'] = message

    response = jsonify(body)
    response.status_code = status_code

    return response

