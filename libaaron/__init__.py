from .libaaron import (
    reify,
    cached,
    w,
    DotDict,
    flatten,
    deepupdate,
    quietinterrupt,
    PBytes,
    mkdummy,
    unpacktsv,
    chunkprocess,
    chunkiter,
    printtsv,
    pipe,
    pipeline,
    fcompose,
    pmap,
    pfilter,
    preduce,
    getrepr,
)

try:
    from .libaaron import lxml_little_iter
except ImportError:
    pass
