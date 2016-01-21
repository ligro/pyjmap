from flask import current_app

class MethodException(Exception):
    message = None

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

class InvalidArguments(MethodException):
    def __init__(self):
        super().__init__('invalidArguments')

# This will contains all methods available in the apis
# always use yield, never return

def method1(args):
    """
    example
    """
    yield ["responseFromMethod1", {"arg1": 3, "arg2": "foo"}]

def method2(args):
    """
    example
    """
    yield ["responseFromMethod2", {"isBlah": True}]
    yield ["anotherResponseFromMethod2", {"data": 10, "yetmoredata": "Hello"}]

