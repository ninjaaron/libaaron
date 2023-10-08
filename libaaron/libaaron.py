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
from typing import (
    cast,
    Callable,
    ContextManager,
    Concatenate,
    IO,
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    Sequence,
    Tuple,
    TypeVar,
    ParamSpec,
    Generic,
)
from typing_extensions import reveal_type

# pylint: disable=invalid-name
T = TypeVar("T")
S = TypeVar("S")
P = ParamSpec("P")


class reify(Generic[T, S]):
    # pylint: disable=too-few-public-methods
    """Use as a class method decorator.  It operates almost exactly like the
    Python ``@property`` decorator, but it puts the result of the method it
    decorates into the instance dict after the first call, effectively
    replacing the function it decorates with an instance variable.  It is, in
    Python parlance, a non-data descriptor.

    Stolen from pyramid.
    http://docs.pylonsproject.org/projects/pyramid/en/latest/api/decorator.html#pyramid.decorator.reify
    """

    def __init__(self, wrapped: Callable[[S], T]):
        self.wrapped = wrapped
        functools.update_wrapper(self, wrapped)

    def __get__(self, inst: S, objtype: type | None = None) -> T:
        if inst is None:
            return self
        val = self.wrapped(inst)
        setattr(inst, self.wrapped.__name__, val)
        return val


def w(iterable: ContextManager[Iterable[T]]) -> Iterator[T]:
    """yields from an iterable with its context manager."""
    with iterable as it:
        yield from it


def chunkiter(iterable: Iterable[T], chunksize: int) -> Iterator[list[T]]:
    """break an iterable into chunks and yield those chunks as lists
    until there's nothing left to yeild.
    """
    iterator = iter(iterable)
    return iter(
        lambda: list(itertools.islice(iterator, chunksize)), []
    )


def chunkprocess(
        func: Callable[Concatenate[Iterable[T], P], S]
) -> Callable[Concatenate[Iterable[T], int, P], Iterator[S]]:
    """take a function that takes an iterable as the first argument.
    return a wrapper that will break an iterable into chunks using
    chunkiter and run each chunk in function, yielding the value of each
    function call as an iterator.
    """

    @functools.wraps(func)
    def wrapper(
            iterable: Iterable[T],
            chunksize: int, /,
            *args: P.args,
            **kwargs: P.kwargs,
    ) -> Iterator[S]:
        for chunk in chunkiter(iterable, chunksize):
            yield func(chunk, *args, **kwargs)

    return wrapper


def longchain(iterables: Iterable[Iterable[T]]) -> Iterator[T]:
    """chain an artibrary number of iterables. (no *args, unlike
    itertools.chain.)
    """
    for iterable in iterables:
        yield from iterable


def getrepr(obj: object, *args: T) -> str:
    """generate generic reprs for objects."""
    classname = obj.__class__.__name__
    argstr = ", ".join(map(repr, args))
    return "{}({})".format(classname, argstr)


def quietinterrupt(msg: str | None = None) -> None:
    """add a handler for SIGINT that optionally prints a given message.
    For stopping scripts without having to see the stacktrace.
    """

    def handler(*args, **kwargs):  # type: ignore
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

    def __str__(self) -> str:
        n, u = self.human_readable()
        if u == "B":
            return str(n) + " bytes"

        return "%.1f %siB" % (n, u)

    def __repr__(self) -> str:
        return getrepr(self, int(self))

    def human_readable(self, decimal: bool = False) -> Tuple[float, str]:
        """returns the size of size as a tuple of:

            (number, single-letter-unit)

        If the decimal flag is set to true, units 1000 is used as the
        divisor, rather than 1024.
        """
        divisor = 1000 if decimal else 1024
        number = float(self)
        unit = ""
        for unit in self.units:
            if number < divisor:
                break
            number /= divisor
        return number, unit.upper()

    @classmethod
    def from_str(
            cls,
            human_readable_str: str,
            decimal: bool = False,
            bits: bool = False
    ) -> 'PBytes':
        """attempt to parse a size in bytes from a human-readable string."""
        divisor = 1000 if decimal else 1024
        num_chars = []
        c = ""
        for c in human_readable_str:
            if c not in cls.digits:
                break
            num_chars.append(c)
        num_str = "".join(num_chars)
        try:
            num = int(num_str)  # type: int | float
        except ValueError:
            num = float(num)
        if bits:
            num /= 8
        return cls(round(num * divisor ** cls.key[c.lower()]))


def unpacktsv(file: IO[str], sep: str = "\t") -> Iterator[list[str]]:
    """generator for stupidly yielding records from a TSV file"""
    return (line.rstrip().split(sep) for line in file)


def printtsv(
        table: Sequence[Sequence[T]],
        sep: str = "\t",
        file: IO[str] = sys.stdout,
) -> None:
    """stupidly print an iterable of iterables in TSV format"""
    for record in table:
        print(*record, sep=sep, file=file)


def mkdummy(name: str, **attrs: T) -> object:
    """Make a placeholder object that uses its own name for its repr"""
    return type(
        name, (), dict(__repr__=(lambda self: "<%s>" % name), **attrs)
    )()


def curry(
        func: Callable[Concatenate[T, P], S]
) -> Callable[[T], Callable[P, S]]:
    return lambda x: functools.partial(func, x)


pmap = curry(map)
pfilter = curry(filter)
preduce = curry(functools.reduce)


class reportiter(Generic[T]):
    """take and iterable and call the report hook occasionally as you
    iterate.
    """

    __slots__ = "iter", "report", "count", "frequency"

    def __init__(
        self,
        iterable: Iterable[T],
        frequency: int = 100,
        report: Callable[[int], None] = lambda i: print(i, file=sys.stderr),
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

    def __iter__(self) -> 'reportiter[T]':
        return self

    def __next__(self) -> T:
        self.count += 1
        if not self.count % self.frequency:
            self.report(self.count)
        try:
            return next(self.iter)
        except StopIteration:
            self.report(self.count)
            raise


def simple_repr(obj: object, props: tuple) -> str:  # type: ignore[type-arg]
    return "%s%s" % (obj.__class__.__qualname__, props)


try:
    from lxml import etree
except ImportError as e:
    _err: ImportError | None = e
else:
    _err = None


def lxml_little_iter(
        *args: P.args, **kwargs: P.kwargs
) -> Iterator[tuple[str, etree.ElementBase]]:
    """Use lxml.etree.iterparse to iterate over elements, but clear the
    tree as we iterate.
    """
    if _err:
        raise _err
    context = etree.iterparse(*args, **kwargs)
    for event, element in context:
        yield event, element
        element.clear()
        while element.getprevious() is not None:
            del element.getparent()[0]
