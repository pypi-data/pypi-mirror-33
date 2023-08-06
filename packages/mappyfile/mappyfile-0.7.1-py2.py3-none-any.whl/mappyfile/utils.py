from __future__ import unicode_literals
import codecs
import warnings
import functools
from mappyfile.parser import Parser
from mappyfile.transformer import MapfileToDict
from mappyfile.pprint import PrettyPrinter
from mappyfile.validator import Validator

try:
    from itertools import izip_longest as zip_longest  # py2
except ImportError:
    from itertools import zip_longest  # py3


def deprecated(func):
    """
    From https://stackoverflow.com/questions/2536307/how-do-i-deprecate-python-functions/30253848#30253848
    This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.
    """
    @functools.wraps(func)
    def new_func(*args, **kwargs):
        warnings.simplefilter('always', DeprecationWarning)  # turn off filter
        warnings.warn("Call to deprecated function {}.".format(func.__name__),
                      category=DeprecationWarning,
                      stacklevel=2)
        warnings.simplefilter('default', DeprecationWarning)  # reset filter
        return func(*args, **kwargs)
    return new_func


def open(fn, expand_includes=True, include_comments=False, include_position=False):
    """
    Load a Mapfile from the supplied filename into a Python dictionary

    Parameters
    ----------

    fn: string
        The path to the Mapfile, or partial Mapfile
    expand_includes: boolean
        Load any ``INCLUDE`` files in the MapFile
    include_comments: boolean
         Include or discard comment strings from the Mapfile - *experimental*
    include_position: boolean
         Include the position of the Mapfile tokens in the output

    Returns
    -------
    dict
        A Python dictionary representing the Mapfile in the mappyfile format

    Example
    -------

    To open a Mapfile from a filename and return it as a dictionary object::

        d = mappyfile.open('mymap.map')

    Notes
    -----

    Partial Mapfiles can also be opened, for example a file containing a ``LAYER`` object.

    """
    p = Parser(expand_includes=expand_includes,
               include_comments=include_comments)
    ast = p.parse_file(fn)
    m = MapfileToDict(include_position=include_position,
                      include_comments=include_comments)
    d = m.transform(ast)
    return d


def load(fp, expand_includes=True, include_position=False, include_comments=False):
    """
    Load a Mapfile from a file-like object

    Parameters
    ----------

    fp: file
        A file-like object
    expand_includes: boolean
        Load any ``INCLUDE`` files in the MapFile
    include_comments: boolean
         Include or discard comment strings from the Mapfile - *experimental*
    include_position: boolean
         Include the position of the Mapfile tokens in the output

    Returns
    -------
    dict
        A Python dictionary representing the Mapfile in the mappyfile format

    Example
    -------

    To open a Mapfile from a file and return it as a dictionary object::

        with open('mymap.map') as fp:
            d = mappyfile.load(fp)

    Notes
    -----

    Partial Mapfiles can also be opened, for example a file containing a ``LAYER`` object.
    """
    p = Parser(expand_includes=expand_includes,
               include_comments=include_comments)
    ast = p.load(fp)
    m = MapfileToDict(include_position=include_position,
                      include_comments=include_comments)
    d = m.transform(ast)
    return d


def loads(s, expand_includes=True, include_position=False, include_comments=False):
    """
    Load a Mapfile from a string

    Parameters
    ----------

    s: string
        The Mapfile, or partial Mapfile, text
    expand_includes: boolean
        Load any ``INCLUDE`` files in the MapFile
    include_comments: boolean
         Include or discard comment strings from the Mapfile - *experimental*
    include_position: boolean
         Include the position of the Mapfile tokens in the output

    Returns
    -------
    dict
        A Python dictionary representing the Mapfile in the mappyfile format

    Example
    -------

    To open a Mapfile from a string and return it as a dictionary object::

        s = '''MAP NAME "TEST" END'''

        d = mappyfile.loads(s)
        assert d["name"] == "TEST"

    """
    p = Parser(expand_includes=expand_includes,
               include_comments=include_comments)
    ast = p.parse(s)
    m = MapfileToDict(include_position=include_position,
                      include_comments=include_comments)
    d = m.transform(ast)
    return d


def dump(d, fp, indent=4, spacer=" ", quote='"', newlinechar="\n"):
    """
    Write d (the Mapfile dictionary) as a JSON formatted stream to fp

    :param dictionary d: A Python dictionary based on the the mappyfile schema
    :param fp: A file-like object
    :param integer indent: The number of ``spacer`` characters to indent structures in
                           the Mapfile
    :param string spacer: The character to use for indenting structures in the Mapfile. Typically
                          spaces or tab characters (``\\t``)
    :param string quote: The quote character to use in the Mapfile (double or single quotes)
    :param string newlinechar: The character to to insert newlines in the Mapfile
    """
    map_string = _pprint(d, indent, spacer, quote, newlinechar)
    fp.write(map_string)


@deprecated
def write(d, output_file, indent=4, spacer=" ", quote='"', newlinechar="\n"):
    """
    Write a Mapfile dictionary to a file. The save function should now be used.
    """
    return save(d, output_file, indent, spacer, quote, newlinechar)


def save(d, output_file, indent=4, spacer=" ", quote='"', newlinechar="\n"):
    """
    Write a Mapfile dictionary to a file.

    :param dictionary d: A Python dictionary based on the the mappyfile schema
    :param string output_file: The output filename
    :param integer indent: The number of ``spacer`` characters to indent structures in
                           the Mapfile
    :param string spacer: The character to use for indenting structures in the Mapfile. Typically
                          spaces or tab characters (``\\t``)
    :param string quote: The quote character to use in the Mapfile (double or single quotes)
    :param string newlinechar: The character to to insert newlines in the Mapfile
    """
    map_string = _pprint(d, indent, spacer, quote, newlinechar)
    _save(output_file, map_string)
    return output_file


def dumps(d, indent=4, spacer=" ", quote='"', newlinechar="\n"):
    """
    Output a Mapfile dictionary as a string

    :param dictionary d: A Python dictionary based on the the mappyfile schema
    :param integer indent: The number of ``spacer`` characters to indent structures in
                           the Mapfile
    :param string spacer: The character to use for indenting structures in the Mapfile. Typically
                          spaces or tab characters (``\\t``)
    :param string quote: The quote character to use in the Mapfile (double or single quotes)
    :param string newlinechar: The character to to insert newlines in the Mapfile
    """
    return _pprint(d, indent, spacer, quote, newlinechar)


def find(lst, key, value):
    """
    Find an item in a list of dicts using a key and a value

    :param list lst: A list of composite dictionaries e.g. ``layers``, ``classes``
    :param string key: The key name to search each dictionary in the list
    :param value: The value to search for
    """
    return next((item for item in lst if item[key.lower()] == value), None)


def findall(lst, key, value):
    """
    Find all items in lst where key matches value.
    For example find all ``LAYER``s in a ``MAP`` where ``GROUP`` equals ``VALUE``

    :param list lst: A list of composite dictionaries e.g. ``layers``, ``classes``
    :param string key: The key name to search each dictionary in the list
    :param value: The value to search for
    """
    possible_values = ("'%s'" % value, '"%s"' % value)
    return (item for item in lst if item[key.lower()] in possible_values)


def findunique(lst, key):
    """
    Find all unique key values for items in lst.

    Parameters
    ----------

    lst: list
         A list of composite dictionaries e.g. ``layers``, ``classes``
    key: string
        The key name to search each dictionary in the list

    Example
    -------

    To find all ``GROUP`` values for ``CLASS`` in a ``LAYER``::

        s = '''
        LAYER
            CLASS
                GROUP "group1"
                NAME "Class1"
                COLOR 0 0 0
            END
            CLASS
                GROUP "group2"
                NAME "Class2"
                COLOR 0 0 0
            END
            CLASS
                GROUP "group1"
                NAME "Class3"
                COLOR 0 0 0
            END
        END
        '''

        d = mappyfile.loads(s)
        groups = mappyfile.findunique(d["classes"], "group")
        assert groups == ["group1", "group2"]
    """
    return sorted(set([item[key.lower()] for item in lst]))


def findkey(d, *keys):
    """
    Get a value from a dictionary based on a list of keys and/or list indexes

    Parameters
    ----------

    d: dict
        A Python dictionary
    keys: list
        A list of key names

    Example
    -------

    To find the value of the first class in the first layer in a Mapfile::

            s = '''
            MAP
                LAYER
                    NAME "Layer1"
                    TYPE POLYGON
                    CLASS
                        NAME "Class1"
                        COLOR 0 0 255
                    END
                END
            END
            '''

            d = mappyfile.loads(s)

            pth = ["layers", 0, "classes", 0]
            cmp = mappyfile.findkey(d, *pth)
            assert cmp["name"] == "Class1"
    """
    if keys:
        keys = list(keys)
        key = keys.pop(0)
        return findkey(d[key], *keys)
    else:
        return d


def validate(d):
    """
    Validate a mappyfile dictionary by using the Mapfile schema

    :param dictionary d: A Python dictionary based on the the mappyfile schema
    """
    v = Validator()
    return v.validate(d)


def update(d1, d2):
    """
    Update dict d1 with properties from d2

    Note
    ----

    Allows deletion of objects with a special "__delete__" key
    For any list of dicts new items can be added when updating

    Parameters
    ----------

        d1: dict
            A Python dictionary
        d2: dict
            A Python dictionary that will be used to update any keys with the same name in d1

    Returns
    -------
    dict
        The updated dictionary

    """
    NoneType = type(None)

    if d2.get("__delete__", False):
        return {}

    for k, v in d2.items():
        if isinstance(v, dict):
            if v.get("__delete__", False):
                # allow a __delete__ property to be set to delete objects
                del d1[k]
            else:
                d1[k] = update(d1.get(k, {}), v)
        elif isinstance(v, (tuple, list)) and all(isinstance(li, (NoneType, dict)) for li in v):
            # a list of dicts and/or NoneType
            orig_list = d1.get(k, [])
            new_list = []
            pairs = list(zip_longest(orig_list, v, fillvalue=None))
            for orig_item, new_item in pairs:
                if orig_item is None:
                    orig_item = {}  # can't use {} for fillvalue as only one dict created/modified!
                if new_item is None:
                    new_item = {}

                if new_item.get("__delete__", False):
                    d = None  # orig_list.remove(orig_item) # remove the item to delete
                else:
                    d = update(orig_item, new_item)

                if d is not None:
                    new_list.append(d)
            d1[k] = new_list
        else:
            if k in d1 and v == "__delete__":
                del d1[k]
            else:
                d1[k] = v
    return d1


def _save(output_file, map_string):
    with codecs.open(output_file, "w", encoding="utf-8") as f:
        f.write(map_string)


def _pprint(d, indent, spacer, quote, newlinechar):
    pp = PrettyPrinter(indent=indent, spacer=spacer,
                       quote=quote, newlinechar=newlinechar)
    return pp.pprint(d)
