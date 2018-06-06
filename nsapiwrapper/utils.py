""" Useful functions for dealing with the API response"""

from xmltodict import parse


def _parsedict(x, dicttype=dict):
    """
    This function recursively loops through the processed xml (now dicttype)
    it unorderers Ordereddicttypes and converts them to regular dicttypeionaries
    """
    if isinstance(x, list):
        gen_list = [dicttype(_parsedicttype(y)) if isinstance(
            _parsedicttype(y), dicttype) else _parsedicttype(y) for y in x]
        return gen_list
    if isinstance(x, str):
        return x
    if isinstance(x, dicttype):
        newdicttype = {}
        for key in x.keys():
            if key[0] in ["@", "#"]:
                thiskey = key[1:].lower()
            else:
                thiskey = key.lower()
            this_lower = _parsedicttype(x[key])
            newdicttype[thiskey] = dicttype(this_lower) if isinstance(
                this_lower, dicttype) else this_lower
        return newdicttype
    if x is None:
        return None

def parsetree(xml):
    """Converts xml to a simple dicttypeionary"""
    return _parsedicttype(parse(xml))
