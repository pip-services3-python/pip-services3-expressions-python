# -*- coding: utf-8 -*-

from pip_services3_commons.errors import BadRequestException


class ExpressionException(BadRequestException):
    """
    Exception that can be thrown by Expression Calculator.
    """

    def __init__(self, correlation_id=None, code=None, message=None, line=0, column=0):
        if line != 0 or column != 0:
            message = f"{message} at line {line} and column {column}"
        super(ExpressionException, self).__init__(correlation_id, code, message)
