"""libaaron is a bunch of reasonably trivially implemented functions that
I find generally useful and don't like having to copy around to different
places every time I want them. I guess it's my own personal "standard
library". It is stronly recommended that you don't depend on this library
directly if your name is not Aaron Christianson, but you may feel free to
copy anything you like.
"""
import functools
import itertools
import signal
import string
import sys
from collections import abc

# pylint: disable=invalid-name


class reify:
    # pylint: disable=too-few-public-methods
    """Use as a class method decorator.  It operates almost exactly like the
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


def w(iterable):
    """yields from an iterable with its context manager."""
    with iterable:
        yield from iterable


def chunkiter(iterable, chunksize):
    """break an iterable into chunks and yield those chunks as lists
    until there's nothing left to yeild.
    """
    iterator = iter(iterable)
    for chunk in iter(lambda: list(itertools.islice(iterator, chunksize)), []):
        yield chunk


def chunkprocess(func):
    """take a function that taks an iterable as the first argument.
    return a wrapper that will break an iterable into chunks using
    chunkiter and run each chunk in function, yielding the value of each
    function call as an iterator.
    """

    @functools.wraps(func)
    def wrapper(iterable, chunksize, *args, **kwargs):
        for chunk in chunkiter(iterable, chunksize):
            yield func(chunk, *args, **kwargs)

    return wrapper


def longchain(iterables):
    """chain an artibrary number of iterables. (no *args, unlike
    itertools.chain.)
    """
    for iterable in iterables:
        yield from iterable


def getrepr(obj, *args):
    classname = obj.__class__.__name__
    argstr = ", ".join(map(repr, args))
    return "{}({})".format(classname, argstr)


class DotDict(dict):
    """dict for people who are too lazy to type brackets and quotation
    marks
    """

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


def deepupdate(
    mapping: abc.MutableMapping, other: abc.Mapping, listextend=False
):
    """update one dictionary from another recursively. Only individual
    values will be overwritten--not entire branches of nested
    dictionaries.
    """

    def inner(other, previouskeys):
        """previouskeys is a tuple that stores all the names of keys
        we've recursed into so far so it can they can be looked up
        recursively on the pimary mapping when a value needs updateing.
        """
        for key, value in other.items():
            if isinstance(value, abc.Mapping):
                inner(value, (*previouskeys, key))

            else:
                node = mapping
                for previouskey in previouskeys:
                    node = node.setdefault(previouskey, {})
                target = node.get(key)
                if (
                    listextend
                    and isinstance(target, abc.MutableSequence)
                    and isinstance(value, abc.Sequence)
                ):
                    target.extend(value)
                else:
                    node[key] = value

    inner(other, ())


def quietinterrupt(msg=None):
    """add a handler for SIGINT that optionally prints a given message.
    For stopping scripts without having to see the stacktrace.
    """

    def handler():
        if msg:
            print(msg, file=sys.stderr)
        sys.exit(1)

    signal.signal(signal.SIGINT, handler)


class PBytes(int):
    """child class of int to facilitate conversion between memory
    representations in bytes and human readable formats. Mostly for
    pretty printing, but it can also parse approximate numbers of bytes
    from a human_readable string.
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

        return "%.1f %siB" % (n, u)

    def __repr__(self):
        return "%s(%r)" % (self.__class__.__name__, int(self))

    def human_readable(self, decimal=False):
        """returns the size of size as a tuple of:

            (number, single-letter-unit)

        If the decimal flag is set to true, units 1000 is used as the
        divisor, rather than 1024.
        """
        divisor = 1000 if decimal else 1024
        number = int(self)
        unit = ""
        for unit in self.units:
            if number < divisor:
                break
            number /= divisor
        return number, unit.upper()

    @classmethod
    def from_str(cls, human_readable_str, decimal=False, bits=False):
        """attempt to parse a size in bytes from a human-readable string."""
        divisor = 1000 if decimal else 1024
        num = []
        c = ""
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
    """generator for stupidly yielding records from a TSV file"""
    return (line.rstrip().split(sep) for line in file)


def printtsv(table, sep="\t", file=sys.stdout):
    """stupidly print an iterable of iterables in TSV format"""
    for record in table:
        print(*record, sep=sep, file=file)


def mkdummy(name, **attrs):
    """Make a placeholder object that uses its own name for its repr"""
    return type(
        name, (), dict(__repr__=(lambda self: "<%s>" % name), **attrs)
    )()


def pipe(value, *functions, funcs=None):
    """pipe(value, f, g, h) == h(g(f(value)))"""
    if funcs:
        functions = funcs
    for function in functions:
        value = function(value)
    return value


def pipeline(*functions, funcs=None):
    """like pipe, but curried:

        pipline(f, g, h)(*args, **kwargs) == h(g(f(*args, **kwargs)))
    """
    if funcs:
        functions = funcs
    head, *tail = functions
    return lambda *args, **kwargs: pipe(head(*args, **kwargs), funcs=tail)


def fcompose(*functions):
    """fcompose(f, g, h)(*args, **kwargs) == f(g(h(*args, **kwargs)"""
    return pipeline(funcs=reversed(functions))


def pmap(func):
    """shorthand for functools.partial(map, func), for use with
    pipelines.
    """
    return functools.partial(map, func)


def pfilter(func):
    """shorthand for functools.partial(filter, func), for use with
    pipelines.
    """
    return functools.partial(filter, func)


def preduce(func):
    """shorthand for functools.partial(functools.reduce, func), for use
    with pipelines.
    """
    return functools.partial(functools.reduce, func)


class reportiter:
    """take and iterable and call the report hook occasionally as you
    iterate.
    """

    __slots__ = "iter", "report", "count", "frequency"

    def __init__(
        self,
        iterable,
        frequency=100,
        report=lambda i: print(i, file=sys.stderr),
    ):
        """
        - iterable: something to iterate on
        - frequency: how often to call the report hook
        - report: function to call every `frequency` iterations
          default is printing the count to stderr.
        """
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
