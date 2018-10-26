import functools
import inspect


def curry(func):
    sig = inspect.signature(func)
    params = []
    for param in sig.parameters.values():
        if (
                param.default is not param.empty or param.kind in
                (param.VAR_POSITIONAL, param.VAR_KEYWORD)
        ):
            break
        params.append(param)
