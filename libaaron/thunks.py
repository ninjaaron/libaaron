def fold(f, init, thunk):
    val = thunk()
    while val is not None:
        hd, tl = val
        init = f(init, hd)
        val = tl()
    return init


def bind(thunk, f):
    def _():
        val = thunk()
        return None if val is None else f(*val)
    return _


def map(f, thunk):
    return bind(thunk, lambda hd, tl: (f(hd), map(f, tl)))


def filter(f, thunk):
    return bind(
        thunk, lambda hd, tl: (hd, filter(f, tl)) if f(hd) else filter(f, tl)()
    )


def take(n, thunk):
    return bind(thunk, lambda hd, tl: None if n == 0 else (hd, take(n-1, tl)))


def takewhile(cond, thunk):
    return bind(
        thunk, lambda hd, tl: (hd, takewhile(cond, tl)) if cond(hd) else None
    )


def zip(xs, ys):
    val1, val2 = xs(), ys()
    if val1 is None or val2 is None:
        return lambda: None
    (x, xs), (y, ys) = val1, val2
    return lambda: (x, y), zip(xs, ys)


def conj(lst, el):
    lst.append(el)
    return lst
