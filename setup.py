from setuptools import setup

package = 'libaaron'
version = '0.2'
with open('README.rst') as fh:
    long_description = fh.read()

setup(name=package,
      version=version,
      description='Functions I like to pack along for various things',
      long_description=long_description,
      url='https://github.com/ninjaaron/libaaron',
      packages=['libaaron'],
      python_requires='>=3.5')
