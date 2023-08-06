import yaml



class AttrDict(dict):

    @classmethod
    def _k(cls, key):
        return key.lower() if isinstance(key, str) else key

    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self._convert_keys()

    def __getitem__(self, key):
        return super(AttrDict, self).__getitem__(self.__class__._k(key))

    def __setitem__(self, key, value):
        super(AttrDict, self).__setitem__(self.__class__._k(key), value)

    def __delitem__(self, key):
        return super(AttrDict, self).__delitem__(self.__class__._k(key))

    def __contains__(self, key):
        return super(AttrDict, self).__contains__(self.__class__._k(key))

    def has_key(self, key):
        return super(AttrDict, self).has_key(self.__class__._k(key))

    def pop(self, key, *args, **kwargs):
        return super(AttrDict, self).pop(self.__class__._k(key), *args, **kwargs)

    def get(self, key, *args, **kwargs):
        return super(AttrDict, self).get(self.__class__._k(key), *args, **kwargs)

    def setdefault(self, key, *args, **kwargs):
        return super(AttrDict, self).setdefault(self.__class__._k(key), *args, **kwargs)

    def update(self, E={}, **F):
        super(AttrDict, self).update(self.__class__(E))
        super(AttrDict, self).update(self.__class__(**F))

    def _convert_keys(self):
        for k in list(self.keys()):
            v = super(AttrDict, self).pop(k)
            self.__setitem__(k, v)

    def __getattr__(self, attr):
        attr = attr.lower()
        return self[attr]

    def __setattr__(self, attr, value):
        attr= attr.lower()
        self[attr] = value



class Config(AttrDict):
    """

    """
    def __init__(self, config_file=None, init=None):
        if config_file:
            data = yaml.load(open(config_file, "r"))
            for k, v in data.items():
                k = k.lower()
                self[k] = AttrDict(v)

        if init:
            for k,v in init.items():
                k=k.lower()
                self[k] = AttrDict(v)

    def merge(self, config_file=None, init=None):
        if config_file:
            data = yaml.load(open(config_file, "r"))
            self._update(data)
        if init:
            self._update(init)

    def _update(self,data):

        for k, v in data.items():
            k = k.lower()
            if k in self:
                self[k].update(v)
            else:
                self[k] = AttrDict(v)

