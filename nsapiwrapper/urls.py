from ezurl import Url
from collections import OrderedDict

class Shard(object):

    """Shard Object
        :param shard: The shard this object represents (must be string)
            Will use the default one if not supplied

        Kwargs can be used to attach parameters to this shard
            that will be included when the url is generated.

    """

    def __init__(self, shard, **kwargs):
        if isinstance(shard, str):
            self.__call__(shard, **kwargs)
        else:
            raise ShardError(
                "Invalid Argument 'shard' cant be {}".format(type(shard)))

    def __call__(self, shard, **kwargs):
        if not isinstance(shard, str):
            raise ShardError(
                "Invalid Argument 'shard' cant be {}. `shard` can only be {}"
                .format(
                    type(shard), str))

        self.shardname = shard
        self._tags = OrderedDict(kwargs)

    def __repr__(self):
        if self._tags:
            gen_repr = (
                "{pn}={pv}".format(
                    pn=k, pv=v) for k,v in self._tags.items())
            repl_text = ",".join(gen_repr)
            return ("<shard:({ShardName},{tags})>").format(
                ShardName=self.shardname,
                tags=repl_text)
        else:
            return ("<shard:{ShardName}>".format(
                ShardName=self.shardname))

    def __str__(self):
        return self.shardname

    def __eq__(self, n):
        """Used for sets/dicts"""
        tagsnames = tuple(sorted((k for k in self._tags.keys())))
        tagsnvalues = tuple(sorted((v for v in self._tags.values())))
        ntagsnames = tuple(sorted((k for k in n._tags.keys())))
        ntagsnvalues = tuple(sorted((v for v in n._tags.values())))

        return ((self.shardname == n.shardname)
                and (set(tagsnames) == set(ntagsnames))
                and set(tagsnvalues) == set(ntagsnvalues))

    def __hash__(self):
        tagsnames = tuple(sorted((k for k in self._tags.keys())))
        tagsnvalues = tuple(sorted((v for v in self._tags.values())))

        return hash(
            hash(self.shardname) ^
            hash(tagsnames) ^
            hash(tagsnames))

    @property
    def name(self):
        """Returns the Name of the Shard"""
        return self._get_main_value()

    def tail_gen(self):
        """
        Generates the parameters for the url.

        """
        return dict(self._tags)

    def _get_main_value(self):
        return self.shardname



def shard_generator(shards):
    for shard in shards:
        if isinstance(shard, str):
            yield shard
        elif isinstance(shard, Shard):
            yield shard._get_main_value()
        else:
            raise ValueError("Shard can not be type: {}".format(type(shard)))


def shard_object_extract(shards):
    store = dict()
    for shard in shards:
        if isinstance(shard, Shard):
            store.update(shard.tail_gen())
    return store






def shard_generator(shards):
    for shard in shards:
        if isinstance(shard, str):
            yield shard
        elif isinstance(shard, Shard):
            yield shard._get_main_value()
        else:
            raise ShardError("Shard can not be type: {}".format(type(shard)))


def shard_object_extract(shards):
    store = dict()
    for shard in shards:
        if isinstance(shard, Shard):
            store.update(shard.tail_gen())
    return store

class Shard(object):

    """Shard Object
        :param shard: The shard this object represents (must be string)
            Will use the default one if not supplied

        Kwargs can be used to attach parameters to this shard
            that will be included when the url is generated.

    """

    def __init__(self, shard, **kwargs):
        if isinstance(shard, str):
            self.__call__(shard, **kwargs)
        else:
            raise ShardError(
                "Invalid Argument 'shard' cant be {}".format(type(shard)))

    def __call__(self, shard, **kwargs):
        if not isinstance(shard, str):
            raise ShardError(
                "Invalid Argument 'shard' cant be {}. `shard` can only be {}"
                .format(
                    type(shard), str))

        self.shardname = shard
        self._tags = OrderedDict(kwargs)

    def __repr__(self):
        if self._tags:
            gen_repr = (
                "{pn}={pv}".format(
                    pn=k, pv=v) for k,v in self._tags.items())
            repl_text = ",".join(gen_repr)
            return ("<shard:({ShardName},{tags})>").format(
                ShardName=self.shardname,
                tags=repl_text)
        else:
            return ("<shard:{ShardName}>".format(
                ShardName=self.shardname))

    def __str__(self):
        return self.shardname

    def __eq__(self, n):
        """Used for sets/dicts"""
        tagsnames = tuple(sorted((k for k in self._tags.keys())))
        tagsnvalues = tuple(sorted((v for v in self._tags.values())))
        ntagsnames = tuple(sorted((k for k in n._tags.keys())))
        ntagsnvalues = tuple(sorted((v for v in n._tags.values())))

        return ((self.shardname == n.shardname)
                and (set(tagsnames) == set(ntagsnames))
                and set(tagsnvalues) == set(ntagsnvalues))

    def __hash__(self):
        tagsnames = tuple(sorted((k for k in self._tags.keys())))
        tagsnvalues = tuple(sorted((v for v in self._tags.values())))

        return hash(
            hash(self.shardname) ^
            hash(tagsnames) ^
            hash(tagsnames))

    @property
    def name(self):
        """Returns the Name of the Shard"""
        return self._get_main_value()

    def tail_gen(self):
        """
        Generates the parameters for the url.

        """
        return dict(self._tags)

    def _get_main_value(self):
        return self.shardname


API_URL = "www.nationstates.net/cgi-bin/api.cgi"


def gen_url(api, shards, version, API_URL=API_URL):
    if not api[0] == "world":
        url = Url(API_URL).query(**({api[0]: api[1]}))
    else:
        url = Url(API_URL)
    if shards:
        url.query(q=tuple(shard_generator(shards)))
        url.query(
            **shard_object_extract(shards))
    if version:
        url.query(v=version)
    return str(url)
