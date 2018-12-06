import functools
import signal
import string
import sys
from collections import abc


class reify:
    """ Use as a class method decorator.  It operates almost exactly like the
    Python ``@property`` decorator, but it puts the result of the method it
    decorates into the instance dict after the first call, effectively
    replacing the function it decorates with an instance variable.  It is, in
    Python parlance, a non-data descriptor.

    Stolen from pyramid.
    http://docs.pylonsproject.org/projects/pyramid/en/latest/api/decorator.html#pyramid.decorator.reify
    """

    def __init__(self, wrapped):
        self.wrapped = wrapped
        functools.update_wrapper(self, wrapped)

    def __get__(self, inst, objtype=None):
        if inst is None:
            return self
        val = self.wrapped(inst)
        setattr(inst, self.wrapped.__name__, val)
        return val


def cached(method) -> property:
    """alternative to reify and property decorators. caches the value when it's
    generated. It cashes it as instance._name_of_the_property.
    """
    name = "_" + method.__name__

    @property
    def wrapper(self):
        try:
            return getattr(self, name)
        except AttributeError:
            val = method(self)
            setattr(self, name, val)
            return val

    return wrapper


def addfield(dct: dict, key, value):
    """you have a list of dictionaries. append value to the list of key."""
    dct.setdefault(key, []).append(value)


def w(iterable):
    """yields from an iterable with its context manager."""
    with iterable:
        yield from iterable


class DotDict(dict):
    "dict for people who are too lazy to type brackets and quotation marks"
    __slots__ = ()
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __dir__(self):
        return list(self)


def flatten(iterable, map2iter=None):
    """recursively flatten nested objects"""
    if map2iter and isinstance(iterable):
        iterable = map2iter(iterable)

    for item in iterable:
        if isinstance(item, str) or not isinstance(item, abc.Iterable):
            yield item
        else:
            yield from flatten(item, map2iter)


def quietinterrupt(msg=None):
    """add a handler for SIGINT that optionally prints a given message. For
    stopping scripts without having to see the stacktrace.
    """

    def handler(*args):
        if msg:
            print(msg, file=sys.stderr)
        sys.exit(1)

    signal.signal(signal.SIGINT, handler)


class PBytes(int):
    """child class of int to facilitate conversion between memory
    representations in bytes and human readable formats. Mostly for pretty
    printing, but it can also parse approximate numbers of bytes from a
    human_readable string.
    """

    __slots__ = ()
    units = "bkmgtpezy"
    key = {v: i for i, v in enumerate(units)}
    digits = set(string.digits)
    digits.update(". ")

    def __str__(self):
        n, u = self.human_readable()
        if u == "B":
            return str(n) + " bytes"

        return "%.1f %siB" % self.human_readable()

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, int(self))

    def human_readable(self, decimal=False):
        divisor = 1000 if decimal else 1024
        number = int(self)
        for unit in self.units:
            if number < divisor:
                break
            number /= divisor
        return number, unit.upper()

    @classmethod
    def from_str(cls, human_readable_str, decimal=False, bits=False):
        divisor = 1000 if decimal else 1024
        num = []
        for c in human_readable_str:
            if c not in cls.digits:
                break
            num.append(c)
        num = "".join(num)
        try:
            num = int(num)
        except ValueError:
            num = float(num)
        if bits:
            num /= 8
        return cls(round(num * divisor ** cls.key[c.lower()]))


def unpacktsv(file, sep="\t"):
    return (line.rstrip().split(sep) for line in file)


def printtsv(table, sep="\t", file=sys.stdout):
    for record in table:
        print(*record, sep=sep, file=file)


def mkdummy(name, **attrs):
    """Make a placeholder object that uses its own name for its repr"""
    return type(name, (), dict(__repr__=(lambda self: "<%s>" % name), **attrs))()


def iter_record(record: dict):
    for fname, flist in record.items():
        for field in flist:
            for sname, sublist in field.items():
                for subfield in sublist:
                    yield fname, sname, subfield


class reportiter:
    __slots__ = "iter", "report", "count", "report"

    def __init__(
        self, iterable, frequency=100, report=lambda i: print(i, file=sys.stderr)
    ):
        self.iter = iter(iterable)
        self.report = report
        self.frequency = frequency
        self.count = 0

    def __iter__(self):
        return self

    def __next__(self):
        self.count += 1
        if not self.count % self.frequency:
            self.report(self.count)
        try:
            return next(self.iter)
        except StopIteration:
            self.report(self.count)
            raise


try:
    from lxml import etree
except ImportError:
    pass
else:

    def lxml_little_iter(*args, **kwargs):
        """Use lxml.etree.iterparse to iterate over elements, but clear the
        tree as we iterate.
        """
        context = etree.iterparse(*args, **kwargs)
        for event, element in context:
            yield event, element
            element.clear()
            while element.getprevious() is not None:
                del element.getparent()[0]
