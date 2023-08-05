import os
import yaml
import json
import collections
import xmltodict
import copy


            

            

class Dicto(object):

    def __init__(self, dict_ = {}, **kwargs):

        if not isinstance(dict_, dict):
            raise ValueError("dict_ parameters is not a python dict")
        
        dict_.update(kwargs)

        to_dicto(dict_, dicto = self)


    def __setitem__(self, key, item):
        # self._dict[key] = item
        setattr(self, key, item)

    def __getitem__(self, key):
        return getattr(self, key)

    def __repr__(self):
        return repr(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    def __delitem__(self, key):
        delattr(self, key)

    def __contains__(self, item):
        return hasattr(self, item)

    def __iter__(self):
        return iter(self.__dict__)


def to_dicto(obj, dicto = None):
    
    if isinstance(obj, Dicto):
        return obj
    
    elif isinstance(obj, dict):

        if dicto is None:
            dicto = Dicto()

        for key, value in obj.items():
            
            value = to_dicto(value)

            setattr(dicto, key, value)

        return dicto

    elif isinstance(obj, str):
        return obj

    elif isinstance(obj, list):
        return [ to_dicto(x) for x in obj ]

    elif isinstance(obj, tuple):
        return tuple([ to_dicto(x) for x in obj ])

    elif hasattr(obj, "__iter__"):
        return ( to_dicto(x) for x in obj )

    else:
        return obj
    
def to_dict(obj, dict_ = None):

    if isinstance(obj, dict):
        return obj
    
    elif isinstance(obj, Dicto):

        if dict_ is None:
            dict_ = dict()

        for key, value in obj.__dict__.items():

            dict_[key] = to_dict(value)

        return dict_

    elif isinstance(obj, str):
        return obj

    elif isinstance(obj, list):
        return [ to_dict(x) for x in obj ]

    elif isinstance(obj, tuple):
        return tuple([ to_dict(x) for x in obj ])

    elif hasattr(obj, "__iter__"):
        return ( to_dict(x) for x in obj )

    else:
        return obj



def merge(dicto, other):
    """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``other`` is merged into
    ``dicto``.
    :param dicto: dict onto which the merge is executed
    :param other: dict that is going to merged into dicto
    :return: None
    """
    if not isinstance(dicto, Dicto):
        dicto = Dicto(dicto)

    if not isinstance(other, Dicto):
        other = Dicto(other)

    for k, v in other.__dict__.items():
        if k in dicto and isinstance(dicto[k], Dicto) and isinstance(other[k], Dicto):
            dicto[k] = merge(dicto[k], other[k])
        else:
            dicto[k] = other[k]
    
    return dicto


def load(filepath, as_dicto = True):
    filepath = os.path.realpath(filepath)

    if filepath.endswith(".yaml") or filepath.endswith(".yml"):
        with open(filepath, 'r') as stream:
            dict_ = yaml.load(stream)
    elif filepath.endswith(".json"):
        with open(filepath, 'r') as stream:
            dict_ = json.load(stream)
    elif filepath.endswith(".xml"):
        with open(filepath, 'r') as stream:
            dict_ = xmltodict.parse(stream.read())
    else:
        raise Exception("File type not supported.")

    if as_dicto:
        return to_dicto(dict_)
    else:
        return dict_

def dump(dicto, filepath):
    
    filepath = os.path.realpath(filepath)
    obj = to_dict(dicto)

    if filepath.endswith(".yaml") or filepath.endswith(".yml"):
        with open(filepath, 'w') as stream:
            yaml.safe_dump(obj, stream, default_flow_style=False)
    elif filepath.endswith(".json"):
        with open(filepath, 'w') as stream:
            json.dump(obj, stream)
    else:
        raise Exception("File type not supported.")


def click_options_config(config_path, single_argument = None, as_dicto = True, underscore_to_dash = True):
    import click

    dict_ = load(config_path, as_dicto=False)

    if not isinstance(dict_, dict):
        raise TypeError("File {config_path} was loaded as a {type}, expected a dict.".format(config_path=config_path, type=type(dict_)))

    def decorator(f):
        for flag, kwargs in dict_.items():

            op_flag = flag.replace('_', '-') if underscore_to_dash else flag
            op_flag = "--" + op_flag

            if not isinstance(kwargs, dict):
                kwargs = dict(default = kwargs)
            
            if "default" in kwargs and not "type" in kwargs:
                kwargs["type"] = type(kwargs["default"])

            f = click.option(op_flag, **kwargs)(f)

        
        if single_argument is not None:
            params = Dicto() if as_dicto else dict()

            def final_f(*args, **final_kwargs):
                
                for kwarg in dict_:
                    kwarg = kwarg.replace("-", "_")

                    if kwarg in final_kwargs:
                        params[kwarg] = final_kwargs.pop(kwarg)

                final_kwargs[single_argument] = params

                return f(*args, **final_kwargs)

            final_f.__click_params__ = f.__click_params__
        else:
            final_f = f


        return final_f

    return decorator
