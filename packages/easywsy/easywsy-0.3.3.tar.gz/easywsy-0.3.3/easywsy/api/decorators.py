import inspect
import types
from ..check.mixin import _check_attr_method_map
from ..error.check_error import CheckError


class check_dec(object):

    def __init__(self, f, fields, *args, **kwargs):
        self.func = f
        self.fields = fields

    def __call__(self, *args, **kwargs):
        res = self.func(*args, **kwargs)
        return res

    def __get__(self, instance, cls):
        return types.MethodType(self, instance, cls)


class check(object):
    """
    Decorator aimed to map attributes with check methods
    that will then validate the values of those attributes.

    @param fields: List of attribute names the defined method will check
    @type  fields: list
    @return: Newly defined method
    @rtype : function
    """

    def __init__(self, fields=[]):
        if not fields or not all(map(lambda x: isinstance(x, str),
                                     fields)):
            msg = ("Check decorator should receive a list of " +
                   "attributes to check.\nGot %s instead" % fields)
            raise CheckError(message=msg)
        self.fields = fields

    def __call__(self, func, *args, **kwargs):
        ins = check_dec(func, self.fields, *args, **kwargs)
        for f in self.fields:
            _check_attr_method_map[f] = [ins, inspect.getargspec(ins.func)[0]]
        return ins
