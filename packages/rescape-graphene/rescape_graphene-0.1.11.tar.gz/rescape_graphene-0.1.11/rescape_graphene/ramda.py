from inspect import isfunction
import itertools
from deepmerge import Merger
from pyramda import *
from json import dumps

# Correcting to match ramda name
prop = getitem


@curry
def filter_dict(f, dct):
    """
        Filter a dict
    :param f: lambda or function expecting a tuple (key, value)
    :param dict:
    :return: The filtered dict
    """
    return dict(filter(f, dct.items()))


def compact_dict(dct):
    """
        Compacts a dct by removing pairs with a None value
    :param dct:
    :return: The filtered dict
    """
    return dict(filter(lambda key_value: key_value[1], dct.items()))


@curry
def prop_or(default, key, dct):
    """
        Ramda propOr implmentation
    :param default:
    :param key:
    :param dct:
    :return:
    """
    return dct[key] if key in dct else default


@curry
def prop_eq(key, value, dct):
    """
        Ramda propEq implementation
    :param key:
    :param value:
    :param dct:
    :return: True if dct[key] is non null and equal to value
    """
    return prop_eq_or(False, key, value, dct)


@curry
def prop_eq_or(default, key, value, dct):
    """
        Ramda propEq plus propOr implementation
    :param default:
    :param key:
    :param value:
    :param dct:
    :return:
    """
    return dct[key] and dct[key] == value if key in dct else default


@curry
def prop_eq_or_in(key, value, dct):
    """
        Ramda propEq/propIn
    :param key:
    :param value:
    :param dct:
    :return:
    """
    return prop_eq_or_in_or(False, key, value, dct)

@curry
def prop_eq_or_in_or(default, key, value, dct):
    """
        Ramda propEq/propIn plus propOr
    :param default:
    :param key:
    :param value:
    :param dct:
    :return:
    """
    return has(key, dct) and \
           (dct[key] == value if key in dct else (
               dct[key] in value if isinstance(value, (list, tuple)) and not isinstance(value, str)
               else default
           ))


@curry
def default_to(default, value):
    """
    Ramda implementation of default_to
    :param default:
    :param value:
    :return:
    """
    return value or default


@curry
def item_path_or(default, keys, dict):
    """
    Optional version of item_path with a default value
    :param default:
    :param keys: List of keys or dot-separated string
    :param dict:
    :return:
    """
    if not keys:
        raise ValueError("Expected at least one key, got {0}".format(keys))
    resolved_keys = keys.split('.') if isinstance(keys, str) else keys
    current_value = dict
    for key in resolved_keys:
        current_value = prop_or(default, key, default_to({}, current_value))
    return current_value

@curry
def item_str_path(keys, dct):
    return item_path(keys.split('.'), dct)

@curry
def has(prop, object_or_dct):
    """
    Implementation of ramda has
    :param prop:
    :param object_or_dct:
    :return:
    """
    return prop in object_or_dct if isinstance(dict, object_or_dct) else hasattr(object_or_dct, prop)

@curry
def omit(omit_props, dct):
    """
    Implementation of omit
    :param omit_props:
    :param dct:
    :return:
    """
    return filter_dict(lambda key_value: key_value[0] not in omit_props, dct)


@curry
def join(strin, items):
    """
        Ramda implementation of join
    :param strin:
    :param items:
    :return:
    """
    return strin.join(map(lambda item: str(item), items))


def dump_json(json):
    """
        Returns pretty-printed json
    :param json
    :return:
    """
    return dumps(json, sort_keys=True, indent=4, separators=(',', ': '))


def head(lst):
    """
        Implementation of Ramda's head
    :param lst:
    :return:
    """
    return lst[0]


@curry
def map_with_obj(f, dct):
    """
        Implementation of Ramda's mapObjIndexed without the final argument.
        This returns the original key with the mapped value, so return a key/value pair and take the values
        to also update the keys
    :param f:
    :param dct:
    :return:
    """
    f_dict = {}
    for k, v in dct.items():
        f_dict[k] = f(k, v)
    return f_dict


@curry
def map_key_values(f, dct):
    """
        Like map_with_obj but expects a key value pair returned from f and uses it to form a new dict
    :param f:
    :param dct:
    :return:
    """
    return from_pairs(values(map_with_obj(f, dct)))


@curry
def map_keys(f, dct):
    """
        Calls f with each key of dct, possibly returning a modified key. Values are unchanged
    :param f: Called with each key and returns the same key or a modified key
    :param dct:
    :return: A dct with keys possibly modifed but values unchanged
    """
    f_dict = {}
    for k, v in dct.items():
        f_dict[f(k)] = v
    return f_dict



def merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    https://stackoverflow.com/questions/38987/how-to-merge-two-dictionaries-in-a-single-expression
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result


def merge_deep(dct1, dct2):
    """
        Deep merge by this spec below
    :param dct1:
    :param dct2:
    :return:
    """
    my_merger = Merger(
        # pass in a list of tuples,with the
        # strategies you are looking to apply
        # to each type.
        [
            (list, ["prepend"]),
            (dict, ["merge"])
        ],
        # next, choose the fallback strategies,
        # applied to all other types:
        ["override"],
        # finally, choose the strategies in
        # the case where the types conflict:
        ["override"]
    )
    return my_merger.merge(dct1, dct2)

@curry
def merge(dct1, dct2):
    """
        Ramda implmentation of merge
    :param dct1:
    :param dct2:
    :return:
    """
    return merge_dicts(dct1, dct2)


def compact(lst):
    """
        Ramda implmentation of compact. Removes Nones from lst (not 0, etc)
    :param lst:
    :return:
    """
    return filter(lambda x: x is not None, lst)


def from_pairs(pairs):
    """
        Implementation of ramda from_paris Converts a list of pairs or tuples of pairs to a dict
    :param pairs:
    :return:
    """
    return {k: v for k, v in pairs}


def flatten(lst):
    """
        Impemenation of ramda flatten
    :param lst:
    :return:
    """
    return list(itertools.chain.from_iterable(lst))


def concat(lst1, lst2):
    """
        Implmentation of ramda cancat
    :param lst1:
    :param lst2:
    :return:
    """
    return lst1 + lst2


def from_pairs_to_array_values(pairs):
    """
        Like from pairs but combines duplicate key values into arrays
    :param pairs:
    :return:
    """
    result = {}
    for pair in pairs:
        result[pair[0]] = concat(prop_or([], pair[0], result), [pair[1]])
    return result


def fullname(o):
    """
    https://stackoverflow.com/questions/2020014/get-fully-qualified-class-name-of-an-object-in-python
    Return the full name of a class
    :param o:
    :return:
    """
    return o.__module__ + "." + o.__class__.__name__

def length(lst):
    """
    Implementation of Ramda length
    :param lst:
    :return:
    """
    return len(lst)


def isalambda(v):
    """
    Detects if something is a lambda
    :param v:
    :return:
    """
    return isfunction(v) and v.__name__ == '<lambda>'


def map_prop_value_as_index(prp, lst):
    """
        Returns the given prop of each item in the list
    :param prp:
    :param lst:
    :return:
    """
    return from_pairs(map(lambda item: (prop(prp, item), item), lst))
