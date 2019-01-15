libaaron
========

Just my library of handy functions I like to bring along. Other people
may feel free to copy this library, but they should not depend on it.
The content and APIs are subject to change without notice.

.. contents::

``reify`` 
----------
``reify`` is a decorator I stole from the Pylons project that I like to
use frequently.

from the docstring:

    Use as a class method decorator.  It operates almost exactly like the
    Python ``@property`` decorator, but it puts the result of the method it
    decorates into the instance dict after the first call, effectively
    replacing the function it decorates with an instance variable.  It is, in
    Python parlance, a non-data descriptor.

``cached``
----------

``cached`` is a decorator that makes a property but caches its results.
It's functionally similar to reify, but it dynamically creates a
"private" attribute to cache the result instead of messing with
descriptors. This approach is comppatible with slots. I love slots.

``w``
-----
``w`` is a function that takes an iterable with a context manager (like
a file object) and yields from that iterable inside its context manager.

.. code:: python

  >>> # instead of this:
  >>> with open('myfile.txt') as mf:
  ...     for line in mf:
  ...         # do something
  ...
  >>> # you can do this:
  >>> for line in w(open('myfile.txt')):
  ...     # do something
  ...
 
``flatten``
-----------
``flatten`` is a function that takes an iterable as an arguments and
recursively yields all contents from nested iterables (except strings,
which are yielded as strings). The optional second argument is a
function that will be used to convert any mappings into iterables before
yielding from them (in the event you want to yield from their values or
something else).

``deepupdate``
--------------
Updates a dictionary from another dictionary, but doesn't overwrite
entire branches of a tree in the case of nested dictionaries. I use it
to combine the content from the system configuration file with a user
configuration file.

.. code:: python

   >>> import libaaron
   >>> a = {
   ...     "type": "foo",
   ...     "content": {
   ...         "bar": "baz",
   ...         "eggs": "spam"
   ...     }
   ... }
   >>> b = {
   ...     "content": {
   ...         "ham": "sausage",
   ...         "bar": "lol"
   ...     }
   ... }
   >>> libaaron.deepupdate(a, b)
   >>> a
   {
       'type': 'foo',
       'content': {
           'bar': 'lol',
           'eggs': 'spam',
           'ham': 'sausage'
        }
   }


There's also a ``listextend`` flag, which, when set to ``True``, if
the value in both dictionaries are sequences, the sequence in ``a``
will be extended with the contents of ``b``. This function can crash
if dictionary a ``b`` has a mapping somewhere that ``a`` simply has
a string.

``quiteinterrupt``
------------------
``quiteinterrupt`` is a function that adds a signal handler which
silences the stacktrace when the a script is stopped with a keyboard
interrupt. It can optionally print a message on interrupt.

``lxml_little_iter``
--------------------
``lxml_little_iter`` is only available if ``lxml`` is in the
environment. It's for iterating over very large xml files with many of
the same kinds of records at the top level (something that would be an
array in JSON). It is for iterating on data that is too large to fit in
memory.

This generator function passes all ``*args`` an ``**kwargs`` to
``lxml.etree.iterparse`` and yields the same ``(even, element)`` tuple.
However, when the next item is retrieved, the previous element will be
cleared and all previous nodes are deleted. Thus, the ram is saved.

``DotDict``
-----------
``DotDict`` is a subclass of dict which allows fetching items with dot
syntax. Useful as an ``object_hook`` when deserializing JSON, perhaps.

``PBytes``
----------
``PBytes`` is a subclass of ``int`` which has a ``__str__`` that shows
interprets it as a number of bytes and make a human readable format. It
can also parse a number of bytes from a string.

.. code:: python

  >>> print(PBytes(2134963))
  2.0 MiB
  >>> PBytes.from_str('35.8 KB')
  PBytes(36659)
  >>> PBytes.from_str('35.8 KB', decimal=True)
  PBytes(35800)

Internally, it's just an integer, so you can do any integer operations
with it. Note that ``from_str`` does not attempt to determine whether it
is a binary or decimal format. Default is binary. Use ``decimal=True``
to explicitely change the behavior.

It also has a ``human_readable`` method which returns a number and the
units for easily constructing alterative representations:

.. code:: python

  >>> PBytes(83629).human_readable()
  (81.6689453125, 'K')
  >>> '%d%s' % PBytes(83629).human_readable()
  '81K'
  >>> '%d%s' % PBytes(83629).human_readable(decimal=True)
  '83K'
