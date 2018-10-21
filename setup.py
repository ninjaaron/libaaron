from setuptools import setup

package = 'libaaron'
version = '0.14'
with open('README.rst') as fh:
    long_description = fh.read()

setup(name=package,
      version=version,
      description='trivial functions I like to pack along for various things',
      long_description=long_description,
      long_description_content_type='text/x-rst',
      url='https://github.com/ninjaaron/libaaron',
      packages=['libaaron'],
      python_requires='>=3.5')
