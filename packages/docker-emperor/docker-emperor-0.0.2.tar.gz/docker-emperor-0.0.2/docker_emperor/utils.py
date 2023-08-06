import six
import yaml
try:
    from yaml import CLoader as YamlLoader, CDumper as YamlDumper
except ImportError:
    from yaml import Loader as YamlLoader, Dumper as YamlDumper

__all__ = ['memoized_property', 'memoized', 'yamp_load', 'yamp_dump', 'yaml' ]


def yamp_dump(data):
    return yaml.dump(data, Dumper=YamlDumper, default_flow_style=False, indent=4)

def yamp_load(content):
    return yaml.load(content, Loader=YamlLoader)

        
class memoized_property(object):

    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        if doc is None and fget is not None and hasattr(fget, "__doc__"):
            doc = fget.__doc__
        self.__get = fget
        # self.__set = fset
        # self.__del = fdel
        # self.__doc__ = doc
        if fget is not None:
            self._attr_name = '___'+fget.func_name
    
    def __get__(self, inst, type=None):
        if inst is None:
            return self
        if self.__get is None:
            raise AttributeError("unreadable attribute")
        
        if not hasattr(inst, self._attr_name):
            result = self.__get(inst)
            setattr(inst, self._attr_name, result)
        return getattr(inst, self._attr_name)
    
    # def __set__(self, inst, value):
    #     if self.__set is None:
    #         raise AttributeError, "can't set attribute"
    #     delattr(inst, self._attr_name)
    #     return self.__set(inst, value)

    # def __delete__(self, inst):
    #     if self.__del is None:
    #         raise AttributeError, "can't delete attribute"
    #     delattr(inst, self._attr_name)
    #     return self.__del(inst)

class memoized(object):

    def __init__(self, function):
        self._function = function
        self._cacheName = '_cache__' + function.__name__
    def __get__(self, instance, cls=None):
        self._instance = instance
        return self
    def __call__(self, *args, **kwargs):
        cache = self._instance.__dict__.setdefault(self._cacheName, {})
        if cache.has_key(args):
            return cache[args]
        else:
            object = cache[args] = self._function(self._instance, *args, **kwargs)
            return object
# class Combination():

#     def __gt__(self, elm2):

#         elm1 = self

#         # None - None
#         if elm1 is None and elm2 is None:
#             return None

#         # None - str
#         elif elm1 is None and isinstance(elm2, six.string_types):
#             elm1 = elm2

#         # None - dict
#         elif elm1 is None and isinstance(elm2, dict):
#             elm1 = elm2
#             combine(elm1, elm2)

#         # None - List
#         elif elm1 is None and isinstance(elm2, list):
#             elm1 = elm2
#             combine(elm1, elm2)

#         # Dict - Dict
#         elif isinstance(elm1, dict) and isinstance(elm2, dict):
#             for key2, val2 in elm2.items():
#                 val1 = elm1.get(key2, val1)
#                 if val1:
#                     elm1[key2] = val1

#         # List - List
#         elif isinstance(elm1, list) and isinstance(elm2, list):
#             elm1 = list(set(elm2 + elm1))

#         # List - None
#         elif isinstance(elm1, list) and elm2 is None:
#             for ind1, val1 in enumerate(elm1):
#                 elm1[ind1] = combine(ind1, None)

#         # if isinstance(elm1, six.string_types) and elm1 in as_shortcuts:
#         #     elm1 = as_shortcuts[elm1]

#         return elm1

#         return Environment(combine(self, service))

#     def __lt__(self, elm2):
#         return elm2 > self 




def combine(elm1, elm2, *args):

    # elm1 is merge into elm2 with elm1 as the priority
    # elm2 < elm1

    # None - None
    if elm1 is None and elm2 is None:
        return None

    # None - str
    elif elm1 is None and isinstance(elm2, six.string_types):
        elm1 = elm2

    # None - dict
    elif elm1 is None and isinstance(elm2, dict):
        elm1 = elm2
        combine(elm1, elm2)

    # None - List
    elif elm1 is None and isinstance(elm2, list):
        elm1 = elm2
        combine(elm1, elm2)

    # Dict - Dict
    elif isinstance(elm1, dict) and isinstance(elm2, dict):
        for key2, val2 in elm2.items():
            val1 = elm1.get(key2, val2)
            if val1 is not None:
                elm1[key2] = val1

    # List - List
    elif isinstance(elm1, list) and isinstance(elm2, list):
        elm1 = list(set(elm2 + elm1))

    # List - None
    elif isinstance(elm1, list) and elm2 is None:
        for ind1, val1 in enumerate(elm1):
            elm1[ind1] = combine(ind1, None)

    # if isinstance(elm1, six.string_types) and elm1 in as_shortcuts:
    #     elm1 = as_shortcuts[elm1]

    if args:
        return combine(elm1, **args)
    else:
        return elm1
