# This will contains all methods available in the apis
# always use yield, never return

def method1(args):
    yield ["responseFromMethod1", {"arg1": 3, "arg2": "foo"}]

def method2(args):
    yield ["responseFromMethod2", {"isBlah": True}]
    yield ["anotherResponseFromMethod2", {"data": 10, "yetmoredata": "Hello"}]

