import inspect
import sys

def isPython3():
    return sys.version_info.major >= 3


def isClass(obj):
    if not isPython3():
        import new
        return type(obj) is new.classobj or type(obj) is type
    else:
        import inspect
        return inspect.isclass(obj)

def objectIsInstance(obj):
    if not isPython3():
        import new
        return type(obj) is new.instance or (hasattr(obj, "__class__") and hasattr(obj.__class__, "__name__"))
    else:
        import inspect
        return inspect.isclass(obj)


def getMethodSignature(method):
    if isPython3():
        return inspect.getfullargspec(method)
    else:
        return inspect.getargspec(method)