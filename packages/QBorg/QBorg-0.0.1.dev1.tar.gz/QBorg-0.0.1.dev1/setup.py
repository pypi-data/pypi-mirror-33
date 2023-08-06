#!/usr/bin/env python3

import os

from setuptools import setup, find_packages
from codecs import open

try:
    from pip._internal.req import parse_requirements
except ImportError:
    try:
        from pip.req import parse_requirements
    except ImportError:
        raise RuntimeError('Could not find pip requirements parser')


base = os.path.abspath(os.path.dirname(__file__))


def read_file(path):
    """ Read file and return contents """
    with open(path, encoding='utf-8') as f:
        return f.read()


def get_reqs(target):
    """ Parse requirements.txt files and return array """
    reqs = parse_requirements(
        os.path.join(base, 'requirements.d', ('%s.txt' % target)),
        session='hack')
    return [str(r.req) for r in reqs]


def get_meta(name):
    """ Get metadata from qborg/__init__.py """
    import qborg
    return getattr(qborg, name)


setup(
    name='QBorg',
    version=get_meta('__version__'),
    license=get_meta('__license__'),
    description=get_meta('__description__'),
    long_description=read_file(os.path.join(base, 'README.rst')),
    url='https://github.engineering.zhaw.ch/QBorg/QBorg',
    author=get_meta('__author__'),
    author_email='qborg@qborg.rocks',
    maintainer=get_meta('__maintainer__'),
    maintainer_email='maintainer@qborg.rocks',
    classifiers=[
        'Development Status :: 3 - Alpha',
        # 'Development Status :: 4 - Beta',
        # 'Development Status :: 5 - Production/Stable',
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: System :: Archiving',
        'Topic :: System :: Archiving :: Backup',
    ],
    keywords='borg backup restore gui qt',
    packages=find_packages(exclude=['docs', 'icons', 'requirements.d', 'tests']),
    python_requires='>=3.4',
    install_requires=get_reqs('app'),
    extras_require={
        'dev': get_reqs('development'),
        'docs': get_reqs('docs')
    },
    entry_points={
        'console_scripts': [
            'qborg=qborg.qborg:main',
        ],
    },
)
