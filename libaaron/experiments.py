#  === data structures === #
class LinkedList:
    """immutable, singly-linked list based on tuples. For why, I don't know."""
    __slots__ = 'node',

    def __init__(self, *args):
        node = ()
        for arg in reversed(args):
            node = (arg, node)
        self.node = node

    @property
    def head(self):
        return self.node[0]

    @property
    def tail(self):
        new = LinkedList()
        new.node = self.node[1]
        return new

    def __iter__(self):
        node = self.node
        while node:
            head, node = node
            yield head

    def __repr__(self):
        return '{}({})'.format(
            self.__class__.__name__,
            ', '.join(map(repr, self)))

    def __radd__(self, val):
        new = LinkedList()
        new.node = (val, self.node)
        return new


#  ==== crazy tailcall stuff - do not use ====  #
def _ispartial(node):
    try:
        return isinstance(node, tuple) and callable(node[0])
    except IndexError:
        return False


def _mkframe(node):
    frame = []
    while _ispartial(node[-1]):
        frame.append(node[:-1])
        node = node[-1]
    return frame, node


def computeframe(frame, val):
    while frame:
        call, *args = frame.pop()
        val = call(*args, val)
    return val


def tco(initial):
    stack = []
    val = initial
    while _ispartial(val):
        frame, (tailcall, *args) = _mkframe(val)
        stack.append(frame)
        val = tailcall(*args)

    while stack:
        val = computeframe(stack.pop(), val)

    return val
