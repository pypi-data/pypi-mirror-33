#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name='octorest',
    version='0.2.dev4',
    description='Client library for OctoPrint REST API',
    long_description=''.join(open('README.rst').readlines()),
    keywords='octoprint, 3d printing',
    author='Miro Hrončok, Jiří Makarius, Douglas Brion',
    author_email='miro@hroncok.cz, meadowfrey@gmail.com, me@douglasbrion.com',
    license='MIT',
    url='https://github.com/dougbrion/OctoRest',
    packages=[p for p in find_packages() if p != 'tests'],
    install_requires=['requests', 'websocket-client'],
    setup_requires=['pytest-runner'],
    tests_require=['pytest', 'betamax-serializers', 'betamax'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Manufacturing',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Printing',
        'Topic :: Software Development :: Libraries',
        'Topic :: System :: Networking :: Monitoring',
        ]
)
