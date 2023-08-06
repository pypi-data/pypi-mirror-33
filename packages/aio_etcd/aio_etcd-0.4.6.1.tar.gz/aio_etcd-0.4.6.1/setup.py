#!/usr/bin/python3

from setuptools import setup, find_packages
import sys, os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
NEWS = open(os.path.join(here, 'NEWS.txt')).read()

def get_version(fname='aio_etcd/__init__.py'):
    with open(fname) as f:
        for line in f:
            if line.startswith('__VERSION__'):
                return eval(line.split('=')[-1])

version = '0.4.3'

install_requires = [
    'python-etcd',
    'aiohttp',
    'dnspython3',
    'urllib3>=1.7.1',
]

test_requires = [
    'pytest',
]

from setuptools.command.test import test as TestCommand

class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = ['--assert=plain','tests/']

setup(
    name='aio_etcd',
    version='.'.join(str(x) for x in get_version()),
    description="An asynchronous python client for etcd",
    long_description=README,
    classifiers=[
        "Topic :: System :: Distributed Computing",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Topic :: Database :: Front-Ends",
    ],
    keywords='etcd raft distributed log api client',
    author='Matthias Urlichs',
    author_email='matthias@urlichs.de',
    url='http://github.com/M-o-a-T/aio-etcd',
    license='MIT',
    packages=('aio_etcd',),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    tests_require=test_requires,
    test_suite='pytest.collector',
    cmdclass = {'test': PyTest},
)
