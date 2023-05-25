from types import SimpleNamespace
from json import JSONEncoder


class NsEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, SimpleNamespace):
            return obj.__dict__
        return super(NsEncoder, self).default(obj)


def to_obj(d):
    return SimpleNamespace(**d)
