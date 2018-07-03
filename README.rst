libaaron
========

Just I library of handy functions I like to bring along.

``reify`` is a decorator I stole from the Pylons project that I like to
use frequently.

``cached`` is a decorator that makes a property but caches it's results.
It's functionally similar to reify, but it dynamically creates a
"private" attribute to cache the result instead of messing with
descriptors. This approach is comppatible with slots. I love slots.

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
