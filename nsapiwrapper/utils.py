""" Useful functions for dealing with the API response"""

from xmltodict import parse


def _parsedict(x):
    """
    This function recursively loops through the processed xml (now dict)
    it unorderers OrderedDicts and converts them to regular dictionaries
    """
    if isinstance(x, list):
        gen_list = [dict(_parsedict(y)) if isinstance(
            _parsedict(y), dict) else _parsedict(y) for y in x]
        return gen_list
    if isinstance(x, str):
        return x
    if isinstance(x, dict):
        newdict = {}
        for key in x.keys():
            if key[0] in ["@", "#"]:
                thiskey = key[1:].lower()
            else:
                thiskey = key.lower()
            this_lower = _parsedict(x[key])
            newdict[thiskey] = dict(this_lower) if isinstance(
                this_lower, dict) else this_lower
        return newdict
    if x is None:
        return None

def parsetree(xml):
    """Converts xml to a simple dictionary"""
    return _parsedict(parse(xml))
