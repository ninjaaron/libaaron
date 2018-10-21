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
    base = None

    def __prepare__(cls, name, **kwargs):
        return StrangeDict(**kwargs)

    def __new__(cls, name, bases, dct):
        if cls.base:
            return enum.Enum(
                name, ' '.join(v for v in dct.values() if isinstance(v, Arg)))
        cls.base = name

        return super().__new__(cls, name, bases, dict(dct))



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
    ns ={}
    exec(init_template.format(sig, body), ns)
    return ns['__init__']


def struct_repr(self):
    return "{}({})".format(
        self.__class__.__name__,
        ', '.join(
            "{}={!r}".format(k, getattr(self, k)) for k in self.__slots__
        )
    )


def struct_getstate(self):
    return [getattr(self, k) for k in self.__slots__]


def struct_setstate(self, state):
    for k, v in zip(self.__slots__, state):
        object.__setattr__(self, k, v)



def _dict(self):
    dct = {}
    for slot in self.__slots__:
        val = getattr(self, slot)
        if hasattr(val, '_dict'):
            dct[slot] = val._dict()
        else:
            dct[slot] = val


class StructMeta(type):
    base = None

    def __prepare__(cls, name, **kwargs):
        return StrangeDict(**kwargs)

    def __new__(cls, name, bases, dct):
        dct = dict(dct)
        if not cls.base:
            cls.base = name
            return super().__new__(cls, name, bases, dct)

        annotations = dct.get('__annotations__')
        if annotations:
            slots = tuple(annotations)
        else:
            slots = tuple(k for k, v in dct.items() if isinstance(v, Arg))
            for k in slots:
                del dct[k]

        for k, v in (
                ('__slots__', slots),
                ('__init__', mkinit(slots)),
                ('__repr__', struct_repr),
                ('__getstate__', struct_getstate),
                ('__setstate__', struct_setstate),
                ('_dict', _dict),
        ):
            if not k in dct:
                dct[k] = v
        if Frozen in bases:
            dct['__setattr__'] = Frozen.__setattr__
        return type(name, (), dct)


class Struct(metaclass=StructMeta):
    pass


class Immutable(Exception):
    pass


StructMeta.base = None


class Frozen(metaclass=StructMeta):
    def __setattr__(self, attr, value):
       raise Immutable(
           "can't set {0}.{1}. type {0} is immutable.".format(
               self.__class__.__name__,
               attr,
               value
           ))
