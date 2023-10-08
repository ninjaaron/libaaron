from typing import (
    Iterable,
    Iterator,
    MutableSequence,
    Sequence,
    Mapping,
    MutableMapping,
    Callable,
    cast,
    TypeVar,
)

T = TypeVar("T")
S = TypeVar("S")


def cached(method: Callable[[S], T]):
    """alternative to reify and property decorators. caches the value when it's
    generated. It cashes it as instance._name_of_the_property.
    """
    name = "_" + method.__name__

    @property  # type: ignore
    def wrapper(self: S) -> T:
        try:
            return cast(T, getattr(self, name))
        except AttributeError:
            val = method(self)
            setattr(self, name, val)
            return val

    return wrapper


class DotDict(dict):
    """dict for people who are too lazy to type brackets and quotation
    marks
    """

    __slots__ = ()
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__  # type: ignore
    __delattr__ = dict.__delitem__  # type: ignore

    def __dir__(self):
        return list(self)


def flatten(
    iterable: Iterable, map2iter: Callable[[Mapping], Iterable] | None = None
) -> Iterator:
    """recursively flatten nested objects"""
    if map2iter and isinstance(iterable, Mapping):
        iterable = map2iter(iterable)

    for item in iterable:
        if isinstance(item, str) or not isinstance(item, Iterable):
            yield item
        else:
            yield from flatten(item, map2iter)


def deepupdate(
        mapping: MutableMapping,
        other: Mapping,
        listextend=False,
) -> None:
    """update one dictionary from another recursively. Only individual
    values will be overwritten--not entire branches of nested
    dictionaries.
    """

    def inner(other: Mapping, previouskeys):
        """previouskeys is a tuple that stores all the names of keys
        we've recursed into so far so it can they can be looked up
        recursively on the pimary mapping when a value needs updateing.
        """
        for key, value in other.items():
            if isinstance(value, Mapping):
                inner(value, (*previouskeys, key))

            else:
                node = mapping
                for previouskey in previouskeys:
                    node = node.setdefault(previouskey, {})
                target = node.get(key)
                if (
                    listextend
                    and isinstance(target, MutableSequence)
                    and isinstance(value, Sequence)
                ):
                    target.extend(value)
                else:
                    node[key] = value

    inner(other, ())


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


