from collections.abc import Mapping, MutableSequence


class AttrObj:
    def __getattr__(self, item):
        if isinstance(self, Mapping):
            return AttrDict.__build(self[item])
        else:
            raise AttributeError(f"{type(self)}.{item} is not Mapping")

    def __getitem__(self, key):
        returning = super().__getitem__(key)
        if isinstance(returning, Mapping):
            return AttrDict.__build(returning)
        elif isinstance(returning, MutableSequence):
            return AttrSeq.__build(returning)
        else:
            return returning

    @classmethod
    def __build(cls, obj):
        if isinstance(obj, Mapping):
            return AttrDict(obj)
        elif isinstance(obj, MutableSequence):
            return AttrSeq(cls.__build(item) for item in obj)
        else:
            return obj


class AttrDict(AttrObj, dict):
    # def __str__(self):
    #     return "{" + ", ".join(f"{k}, {v}" for k, v in self.items()) + "}"
    pass


class AttrSeq(AttrObj, list):
    # def __str__(self):
    #     return str([str(i) for i in self])
    pass
