import os
import yaml
import json
import collections
import xmltodict
import copy

class Dicto(object):

    def __init__(self, dict_, **kwargs):
        
        dict_.update(kwargs)

        if not isinstance(dict_, dict):
            raise ValueError("dict_ parameters is not a python dict")
        
        for key, value in dict_.items():
            if isinstance(value, Dicto):
                pass

            elif isinstance(value, dict):
                value = Dicto(value)

            elif isinstance(value, str):
                pass

            elif hasattr(value, "__iter__"):
                value = [ Dicto(e) if isinstance(e, dict) else e for e in value ]

            setattr(self, key, value)


    # def __getattr__(self, attr):
        
    #     if attr in self._dict:
    #         return self._dict[attr]
    #     else:
    #         raise AttributeError(attr)

    # def __setattr__(self, attr, value):
    #     self._dict[attr] = value

    def __setitem__(self, key, item):
        # self._dict[key] = item
        setattr(self, key, item)

    def __getitem__(self, key):
        return getattr(self, key)

    def __repr__(self):
        return repr(self.__dict__)

    def __len__(self):
        return len(self.__dict__)

    # def __delitem__(self, key):
    #     del self._dict[key]

    def __cmp__(self, dict_):
        return self.__dict__.__cmp__(dict_)

    def __contains__(self, item):
        return item in self.__dict__

    def __iter__(self):
        return iter(self.__dict__)

    
def to_dict(dicto):
    dict_ = dicto.__dict__.copy()

    for key, value in dict_.items():
        if isinstance(value, Dicto):
            dict_[key] = value.__dict__

        elif isinstance(value, str):
            pass

        elif isinstance(value, dict):
            pass

        elif hasattr(value, "__iter__"):
            dict_[key] = [ e.__dict__ if isinstance(e, Dicto) else e for e in value ]

    return dict_



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
        dict_ = Dicto(dict_)

    return dict_

def dump(dicto, filepath):
    
    filepath = os.path.realpath(filepath)
    obj = dicto.__dict__

    if filepath.endswith(".yaml") or filepath.endswith(".yml"):
        with open(filepath, 'w') as stream:
            yaml.safe_dump(obj, stream, default_flow_style=False)
    elif filepath.endswith(".json"):
        with open(filepath, 'w') as stream:
            json.dump(obj, stream)
    else:
        raise Exception("File type not supported.")


def click_options_config(config_path, single_argument = None):
    import click

    dict_ = load(config_path, as_dicto=False)

    def decorator(f):
        for flag, kwargs in dict_.items():
            op_flag = "--" + flag

            if not isinstance(kwargs, dict):
                kwargs = dict(default = kwargs)
            
            if "default" in kwargs and not "type" in kwargs:
                kwargs["type"] = type(kwargs["default"])

            f = click.option(op_flag, **kwargs)(f)

        
        if single_argument is not None:
            params = Dicto({})

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
