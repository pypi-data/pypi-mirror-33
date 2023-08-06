"""
Utility to convert python objects to json array
"""

import json

def dict_to_json_generator(dict_generator):
    """
    :param dict_generator: iterator of dictionary like objects
    :type dict_generator: iter[dict]

    :return: yields str of json objects
    :rtype: iter[str]
    """
    yield "["
    yield json.dumps(next(dict_generator))
    for dict_obj in dict_generator:
        yield ",{}".format(json.dumps(dict_obj))
    yield "]"
