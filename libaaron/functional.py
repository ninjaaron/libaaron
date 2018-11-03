import functools
import inspect
import typing


# def curry(func):
#     sig = inspect.signature(func)
#     params = []
#     for param in sig.parameters.values():
#         if (
#                 param.default is not param.empty or param.kind in
#                 (param.VAR_POSITIONAL, param.VAR_KEYWORD)
#         ):
#             break
#         params.append(param)

class NoDispatch(Exception):
    pass


def param_pair(param):
    if param.annotation == param.empty:
        return param.name, object
    else:
        return param.name, param.annotation


# is broken
def kwargsmatch(annotations, kwargs):
    kwargs = kwargs.copy()
    for name, T in annotations:
        try:
            if not isinstance(kwargs.pop(name), T):
                return False
        except KeyError:
            return False

    if kwargs:
        return False
    return True


def ismatch(annotations, args, kwargs):
    annotations = iter(annotations)
    args = list(zip(args, annotations))
    annotations = list(annotations)
    if not all(isinstance(arg, T) for arg, (_, T) in args):
        return False
    return kwargsmatch(annotations, kwargs)


def multiple_dispatch(func):
    dispatches = []

    def dispatch(_func):
        params = inspect.signature(_func).parameters.values()
        annotations = tuple(map(param_pair, params))
        dispatches.append((_func, annotations))

    def call(*args, **kwargs):
        for _func, annotations in dispatches:
            if ismatch(annotations, args, kwargs):
                return _func(*args, **kwargs)
        raise NoDispatch("Call did not match any dispatch")
        
    dispatch(func)
    call.dispatch = dispatch
    return call


class FList:
    __slots__ = 'head', 'callback', 'args', 'kwargs'

    def __init__(self, head, callback, *args, **kwargs):
        """Linked list that produces the next item from a callback."""
        self.head = head
        self.callback = callback
        self.args = args
        self.kwargs = kwargs

    @property
    def tail(self):
        return self.callback(*self.args, **self.kwargs)

    def __iter__(self):
        node = self
        while isinstance(node, FList):
            yield node.head
            node = node.tail
        yield node
