# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['libaaron']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'libaaron',
    'version': '1.4.4',
    'description': 'trivial functions I like to pack along for various things',
    'long_description': 'libaaron\n========\n\nJust my library of handy functions I like to bring along. Other people\nmay feel free to copy this library, but they should not depend on it.\nThe content and APIs are subject to change without notice.\n\n.. contents::\n\n``reify`` \n----------\n``reify`` is a decorator I stole from the Pylons project that I like to\nuse frequently.\n\nfrom the docstring:\n\n    Use as a class method decorator.  It operates almost exactly like the\n    Python ``@property`` decorator, but it puts the result of the method it\n    decorates into the instance dict after the first call, effectively\n    replacing the function it decorates with an instance variable.  It is, in\n    Python parlance, a non-data descriptor.\n\n``cached``\n----------\n\n``cached`` is a decorator that makes a property but caches its results.\nIt\'s functionally similar to reify, but it dynamically creates a\n"private" attribute to cache the result instead of messing with\ndescriptors. This approach is comppatible with slots. I love slots.\n\n``w``\n-----\n``w`` is a function that takes an iterable with a context manager (like\na file object) and yields from that iterable inside its context manager.\n\n.. code:: python\n\n  >>> # instead of this:\n  >>> with open(\'myfile.txt\') as mf:\n  ...     for line in mf:\n  ...         # do something\n  ...\n  >>> # you can do this:\n  >>> for line in w(open(\'myfile.txt\')):\n  ...     # do something\n  ...\n \n``flatten``\n-----------\n``flatten`` is a function that takes an iterable as an arguments and\nrecursively yields all contents from nested iterables (except strings,\nwhich are yielded as strings). The optional second argument is a\nfunction that will be used to convert any mappings into iterables before\nyielding from them (in the event you want to yield from their values or\nsomething else).\n\n``deepupdate``\n--------------\nUpdates a dictionary from another dictionary, but doesn\'t overwrite\nentire branches of a tree in the case of nested dictionaries. I use it\nto combine the content from the system configuration file with a user\nconfiguration file.\n\n.. code:: python\n\n   >>> import libaaron\n   >>> a = {\n   ...     "type": "foo",\n   ...     "content": {\n   ...         "bar": "baz",\n   ...         "eggs": "spam"\n   ...     }\n   ... }\n   >>> b = {\n   ...     "content": {\n   ...         "ham": "sausage",\n   ...         "bar": "lol"\n   ...     }\n   ... }\n   >>> libaaron.deepupdate(a, b)\n   >>> a\n   {\n       \'type\': \'foo\',\n       \'content\': {\n           \'bar\': \'lol\',\n           \'eggs\': \'spam\',\n           \'ham\': \'sausage\'\n        }\n   }\n\n\nThere\'s also a ``listextend`` flag, which, when set to ``True``, if\nthe value in both dictionaries are sequences, the sequence in ``a``\nwill be extended with the contents of ``b``. This function can crash\nif dictionary a ``b`` has a mapping somewhere that ``a`` simply has\na string.\n\n``pipe``\n------------\n``pipe`` is a trivial function that takes an initial value and any\nnumber of functions as arguments applies them in a compositional manner.\nIt is defined thusly:\n\n.. code:: python\n\n   def pipe(value, *functions):\n       for function in functions:\n           value = function(value)\n       return value\n\n\nTherefore:\n\n.. code:: python\n\n   pipe(value, f, g, h) == h(g(f(value)))\n\nThis is to avoid having to come up with a lot of intermediate variable\nnames on the one hand, or deeply nested function calls on the other.\n\n``pipeline``\n------------\n``pipeline`` is a wrapper on pipe that curries the functions and lets\nyou apply the initial arguments later.\n\n.. code:: python\n\n   pipline(f, g, h)(*args, **kwargs) == h(g(f(*args, **kwargs)))\n\n``fcompose``\n------------\n``fcompose`` gives math-like function composition. It\'s basically\nidentical to ``pipeline``, but with reverse application order.\n\n.. code:: python\n\n   # in math, this would look like `f ∘ g ∘ h`\n   fcompose(f, g, h)(*args, **kwargs) == f(g(h(*args, **kwargs)\n\nNote that there is nothing clever about how ``pipeline`` and\n``fcompose`` work. They aren\'t classes that simulate high-order\nfunctions like ``functools.partial``, they are just normal high order\nfunctions, and building pipelines upon pipelines isn\'t going to optimize\nout the call stack.\n\n``pmap``, ``pfilter`` and ``preduce``\n-------------------------------------\n.. code:: python\n\n   pmap(f) == functools.partial(map, f)\n   pfilter(f) == functools.partial(filter, f)\n   preduce(f) == functools.partial(functools.reduce, f)\n\nJust convenience functions for currying ``map``, ``filter`` and\n``reduce``, which is something which freequently helpful when using the\nabove function composition functions.\n\nAllows stuff like this:\n\n.. code:: python\n\n   import sys\n   from libaaron import pipe, pmap, pfilter\n\n   shout_about_dogs = pipe(\n       sys.stdin,\n       pfilter(lambda line: "dog" in line.lower()),\n       pmap(str.upper)\n   )\n\n   # similar to:\n   shout_about_dogs = (l.upper() for l in sys.stdin if dog in l.lower())\n\nThe comprehension syntax is obviously clearer in this case. ``pipe`` is\nuseful for longer iteration pipelines which can become unclear if\nfactored with comprehensions.\n\n``quiteinterrupt``\n------------------\n``quiteinterrupt`` is a function that adds a signal handler which\nsilences the stacktrace when the a script is stopped with a keyboard\ninterrupt. It can optionally print a message on interrupt.\n\n``lxml_little_iter``\n--------------------\n``lxml_little_iter`` is only available if ``lxml`` is in the\nenvironment. It\'s for iterating over very large xml files with many of\nthe same kinds of records at the top level (something that would be an\narray in JSON). It is for iterating on data that is too large to fit in\nmemory.\n\nThis generator function passes all ``*args`` an ``**kwargs`` to\n``lxml.etree.iterparse`` and yields the same ``(even, element)`` tuple.\nHowever, when the next item is retrieved, the previous element will be\ncleared and all previous nodes are deleted. Thus, the ram is saved.\n\n``DotDict``\n-----------\n``DotDict`` is a subclass of dict which allows fetching items with dot\nsyntax. Useful as an ``object_hook`` when deserializing JSON, perhaps.\n\n``PBytes``\n----------\n``PBytes`` is a subclass of ``int`` which has a ``__str__`` that shows\ninterprets it as a number of bytes and make a human readable format. It\ncan also parse a number of bytes from a string.\n\n.. code:: python\n\n  >>> print(PBytes(2134963))\n  2.0 MiB\n  >>> PBytes.from_str(\'35.8 KB\')\n  PBytes(36659)\n  >>> PBytes.from_str(\'35.8 KB\', decimal=True)\n  PBytes(35800)\n\nInternally, it\'s just an integer, so you can do any integer operations\nwith it. Note that ``from_str`` does not attempt to determine whether it\nis a binary or decimal format. Default is binary. Use ``decimal=True``\nto explicitely change the behavior.\n\nIt also has a ``human_readable`` method which returns a number and the\nunits for easily constructing alterative representations:\n\n.. code:: python\n\n  >>> PBytes(83629).human_readable()\n  (81.6689453125, \'K\')\n  >>> \'%d%s\' % PBytes(83629).human_readable()\n  \'81K\'\n  >>> \'%d%s\' % PBytes(83629).human_readable(decimal=True)\n  \'83K\'\n',
    'author': 'Aaron Christianson',
    'author_email': 'ninjaaron@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ninjaaron/libaaron',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.5,<4.0',
}


setup(**setup_kwargs)
