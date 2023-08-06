# encoding: utf-8

import logging_helper
import json
import re
import random
from functools import wraps
from collections import OrderedDict
from ...config.constants import ModifierConstant


logging = logging_helper.setup_logging()


def parse_dictionary_parameters(modifier):

    def key(parameter):
        return parameter.split(u':')[0]

    def value(parameter):
        return u':'.join(parameter.split(u':')[1:])

    if not modifier[ModifierConstant.params]:
        modifier[ModifierConstant.params] = {}

    else:
        modifier[ModifierConstant.params] = re.sub(r",\s*(\w)",  # Remove Whitespace
                                                   r',\1',  # after comma
                                                   modifier[ModifierConstant.params])

        try:
            modifier[ModifierConstant.params] = {key(parameter): value(parameter)
                                                 for parameter
                                                 in modifier[ModifierConstant.params].split(u',')}

        except (IndexError, ValueError):
            raise ValueError(u"Bad parameters "
                             u"(probably a missing or extra ',' or ':') "
                             u"in {parameters}".format(parameters=modifier[ModifierConstant.params]))

    logging.debug(u'params: {p}'.format(p=modifier))

    return modifier

# ------------------------------------------------------------------------------


TRUE = u'true'
FALSE = u'false'
BOOLEANS = (TRUE, FALSE)


def get_parameter(parameter,
                  modifier,
                  default=None):
    value = None
    try:
        value = modifier[parameter]
    except (IndexError, TypeError, KeyError):
        pass

    try:
        value = modifier[parameter.lower()]
    except (IndexError, TypeError, KeyError, AttributeError):
        pass

    try:
        value = modifier[ModifierConstant.params][parameter]
    except (IndexError, TypeError, KeyError, AttributeError):
        pass

    try:
        value = modifier[ModifierConstant.params][parameter.lower()]
    except (IndexError, TypeError, KeyError, AttributeError):
        pass

    if value is None:
        return default

    return value if value.lower() not in BOOLEANS else value.lower() == TRUE


# -----------------------------------------------------------------------------


def parse_list_parameters(modifier):

    if not modifier[ModifierConstant.params]:
        modifier[ModifierConstant.params] = []
        return
    if not isinstance(modifier[ModifierConstant.params], list):
        modifier[ModifierConstant.params] = re.sub(r",\s*(\w)",  # Remove Whitespace
                                                     r',\1',  # after comma
                                                   modifier[ModifierConstant.params])
        try:
            modifier[ModifierConstant.params] = [value.strip()
                                                 for value
                                                 in modifier[ModifierConstant.params].split(u',')]
        except ValueError:
            raise ValueError(u"Bad parameters (probably a missing"
                             u" or extra ',') in {parameters}".format(parameters=modifier[ModifierConstant.params]))

# -----------------------------------------------------------------------------


def parse_json_parameters(modifier):

    if not isinstance(modifier[ModifierConstant.params], (list, dict)):

        if not modifier[ModifierConstant.params]:
            modifier[ModifierConstant.params] = []
            return

        try:
            modifier[ModifierConstant.params] = json.loads(modifier[ModifierConstant.params])
        except ValueError:
            raise ValueError(u"Bad parameters (probably malformed JSON) "
                             u"in {parameters}".format(parameters=modifier[ModifierConstant.params]))


# -----------------------------------------------------------------------------


def decorate_for_dictionary_parameters(func):

    """
    Calls the modifier after extracting the parameters as a dictionary.

    e.g. parameters[u'parameters'] == u"start:1300, interval:60"
    is converted to parameters[u'parameters'] == {u'start':    u'1300',
                                                  u'interval': u'60"}
    """
    @wraps(func)
    def wrapper(request,
                response,
                modifier):

        # logging.debug(u'in decorate_for dictionary parameters')

        parse_dictionary_parameters(modifier)

        func(request,
             response,
             modifier)

        return response

    return wrapper

# ------------------------------------------------------------------------------


def decorate_for_list_parameters(func):

    """
    Calls the modifier after extracting the parameters as a list.

    e.g. parameters[u'parameters'] == u"1, 2, 3, 4"
    is converted to parameters[u'parameters'] == [u"1", u"2", u"3", u"4"]
    """
    @wraps(func)
    def wrapper(request,
                response,
                modifier):

        # logging.debug(u'in decorate_for list parameters')

        parse_list_parameters(modifier)

        func(request,
             response,
             modifier)

        return response

    return wrapper
# ------------------------------------------------------------------------------


def decorate_for_json_parameters(func):

    """
    Calls the modifier after extracting the parameters as a json string and
    converting to a python object (integer, float, string, list or dictionary)

    e.g. parameters[u'parameters'] == '{"a": [1, 2, 3], "b": "some string"}'
    is converted to parameters[u'parameters'] == {u'a': [1, 2, 3], u'b': u'some string'}
    """
    @wraps(func)
    def wrapper(request,
                response,
                modifier):

        # logging.debug(u'in decorate_for list parameters')

        parse_json_parameters(modifier)

        func(request,
             response,
             modifier)

        return response

    return wrapper


# ------------------------------------------------------------------------------


def decorate_for_json_modifier(func):

    u"""
    calls the modifier with the response content
    already extracted from JSON as an ordered dictionary
    """
    @wraps(func)
    def wrapper(request,
                response,
                modifier):

        # logging.debug(u'in decorate_for_json_modifier')

        try:
            response._content = json.loads(response.content,
                                           object_pairs_hook=OrderedDict)
        except (TypeError, ValueError) as err:
            logging.error(u'Failed loading response to JSON')
            logging.error(err)
            return response

        func(request,
             response,
             modifier)

        response._content = json.dumps(response.content)

        return response

    return wrapper

# ------------------------------------------------------------------------------


def get_hostname_from_url(url):
    return url.split(u'//:')[-1].split(u'/')[0]

# ------------------------------------------------------------------------------


def get_hostname_from_response(response):
    return get_hostname_from_url(response.url)

# ------------------------------------------------------------------------------


def warn_on_invalid_json(json_object):
    try:
        json.loads(json_object)

    except ValueError:
        logging.warning(u'Content is not JSON')

# ------------------------------------------------------------------------------


def unicodify(string):

    u"""
    Replaces ASCII characters in a string with
    a random similar Unicode character

    e.g. 'utf8ify' -> 'ūtf8ífŷ'
    """

    unicode_lookup = {u'A': u'AÀÁÂÄÆÃÅĀ',
                      u'C': u'CĆČ',
                      u'E': u'EÈÉÊËĒĖĘ',
                      u'I': u'IÌĮĪÍÏÎ',
                      u'L': u'LŁ',
                      u'N': u'NŃÑ',
                      u'O': u'OÕŌØŒÓÒÖÔ',
                      u'S': u'SŚŠ',
                      u'U': u'UŪÚÙÜÛ',
                      u'W': u'WŴ',
                      u'Y': u'YŶ',
                      u'Z': u'ZŽŹŻ',

                      u'a': u'aàáâäæãåā',
                      u'c': u'cçćč',
                      u'e': u'eèéêëēėę',
                      u'i': u'iìįīíïî',
                      u'l': u'lł',
                      u'n': u'nńñ',
                      u'o': u'oõōøœóòöô',
                      u's': u'sßśš',
                      u'u': u'uūúùüû',
                      u'w': u'wŵ',
                      u'y': u'yŷ',
                      u'z': u'zžźż',
                      }

    def lookup(character):
        try:
            return random.choice(unicode_lookup[character])

        except KeyError:
            return character

    return u''.join([lookup(c) for c in string])


if __name__ == u"__main__":
    assert get_parameter(u'a',
                         {u'a': u'True', ModifierConstant.params: {u'b': u'signed'}})
    assert get_parameter(u'a',
                         {u'a': u'true', ModifierConstant.params: {u'b': u'Signed'}},
                         u'x')
    assert get_parameter(u'a',
                         {u'a': u'False', ModifierConstant.params: {u'b': u'signed'}}) is False
    assert get_parameter(u'a',
                         {u'a': u'false', ModifierConstant.params: {u'b': u'signed'}}) is False
    assert get_parameter(u'a',
                         {u'a': u'flAnge', ModifierConstant.params: {u'b': u'signed'}}) == u'flAnge'
    assert get_parameter(u'b',
                         {u'a': u'a', ModifierConstant.params: {u'b': u'True'}})
    assert get_parameter(u'b',
                         {u'a': u'a', ModifierConstant.params: {u'b': u'true'}},
                         u'x')
    assert get_parameter(u'b',
                         {u'a': u'a', ModifierConstant.params: {u'b': u'False'}}) is False
    assert get_parameter(u'b',
                         {u'a': u'a', ModifierConstant.params: {u'b': u'false'}}) is False
    assert get_parameter(u'b',
                         {u'a': u'a', ModifierConstant.params: {u'b': u'flAnge'}}) == u'flAnge'
    assert get_parameter(u'c',
                         {u'a': u'a', ModifierConstant.params: {u'b': u'false'}}) is None

    assert get_parameter(u'c',
                         {u'a': u'a', ModifierConstant.params: {u'b': u'flAnge'}},
                         u'default') == u'default'
