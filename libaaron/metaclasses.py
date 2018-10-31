import enum


class Arg(str):
    pass


class StrangeDict(dict):
    __slots__ = ()

    def __missing__(self, key):
        if key == '__name__':
            raise KeyError
        arg = Arg(key)
        self[key] = arg
        return arg


class EnumMeta(type):
    def __prepare__(cls, name, **kwargs):
        return StrangeDict(**kwargs)

    def __new__(cls, name, bases, dct):
        if not bases:
            return super().__new__(cls, name, bases, dict(dct))

        return enum.Enum(
            name,
            ' '.join(v for v in dct.values() if isinstance(v, Arg))
        )


class Enum(metaclass=EnumMeta):
    pass


init_template = '''\
def __init__(self, {}):
    {}
'''


def mkinit(slots):
    sig = ', '.join(slot for slot in slots)
    body = '\n    '.join(
        "object.__setattr__(self, {!r}, {})".format(slot, slot)
        for slot in slots
    )
    ns = {}
    exec(init_template.format(sig, body), ns)
    return ns['__init__']


class Mutablility(Exception):
    pass


class Immutable:
    def __setattr__(self, attr, value):
        raise Mutablility(
            "can't set {0}.{1}. type {0} is immutable.".format(
                self.__class__.__name__,
                attr,
                value
            ))


class StructMeta(type):
    def __prepare__(cls, name, **kwargs):
        return StrangeDict(**kwargs)

    def __new__(cls, name, bases, dct):
        dct = dict(dct)
        if not bases:
            return super().__new__(cls, name, bases, dct)

        annotations = dct.get('__annotations__')
        if annotations:
            slots = tuple(annotations)
        else:
            slots = tuple(k for k, v in dct.items() if isinstance(v, Arg))
            for k in slots:
                del dct[k]

        methods = (kv for base in bases for kv in vars(base).items())
        for k, v in methods:
            if k not in dct:
                dct[k] = v

        dct['__slots__'] = slots
        dct['__init__'] = mkinit(slots)
        return type(name, (), dct)


class Struct(metaclass=StructMeta):
    def __repr__(self):
        return "{}({})".format(
            self.__class__.__name__,
            ', '.join(
                "{}={!r}".format(k, getattr(self, k)) for k in self.__slots__
            )
        )

    def __getstate__(self):
        return [getattr(self, k) for k in self.__slots__]

    def __setstate__(self, state):
        for k, v in zip(self.__slots__, state):
            object.__setattr__(self, k, v)

    def to_dict(self):
        dct = {}
        for slot in self.__slots__:
            val = getattr(self, slot)
            if hasattr(val, '_dict'):
                dct[slot] = val._dict()
            else:
                dct[slot] = val
        return dct
