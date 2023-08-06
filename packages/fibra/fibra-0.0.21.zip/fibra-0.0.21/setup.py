from __future__ import print_function
from __future__ import unicode_literals

try:
    from setuptools import setup, find_packages, Extension
except ImportError:
    print('You need to install setuptools to install this package.')
    raise

packages = find_packages()

setup(
    name = "fibra",
    version = "0.0.21",
    packages = packages,
    url = "http://code.google.com/p/fibra/",
    author='Simon Wittber',
    author_email='simonwittber@gmail.com',
    maintainer='Mario Frasca',
    maintainer_email='mario@anche.no',
    license='MIT',
    platforms=['Any'],
    description="Fibra provides advanced cooperative concurrency using Python generators.",
)

