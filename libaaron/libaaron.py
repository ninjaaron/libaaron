import functools


class reify:
    """ Use as a class method decorator.  It operates almost exactly like the
    Python ``@property`` decorator, but it puts the result of the method it
    decorates into the instance dict after the first call, effectively
    replacing the function it decorates with an instance variable.  It is, in
    Python parlance, a non-data descriptor.

    Stolen from pyramid.
    http://docs.pylonsproject.org/projects/pyramid/en/latest/api/decorator.html#pyramid.decorator.reify
    """
    __slots__ = 'wrapped',

    def __init__(self, wrapped):
        self.wrapped = wrapped
        functools.update_wrapper(self, wrapped)

    def __get__(self, inst, objtype=None):
        if inst is None:
            return self
        val = self.wrapped(inst)
        setattr(inst, self.wrapped.__name__, val)
        return val


def cached(method):
    """alternative to reify and property decorators. caches the value when it's
    generated. It cashes it as _methodname.
    """
    name = '_%s' % method.__name__

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


#  === Dating advice ===  #
MONTHS = {m: i+1 for i, m in enumerate(
    'jan feb mar apr may jun jul aug sep oct nov dec'.split()
)}


class BadDate(Exception):
    pass


def parse_date(string):
    year, month, day = None, None, None
    for field in string.split():
        try:
            val = int(field.rstrip(','))
            if val > 31:
                year = val
            else:
                day = val
        except ValueError:
            month = MONTHS[field[0:3].lower()]

    if not all((year, month, day)):
        raise BadDate((year, month, day))

    return year, month, day
