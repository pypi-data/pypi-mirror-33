# -*- coding: utf-8 -*-
from setuptools import setup

from gitcepter import VERSION

setup(
    name='gitcepter',
    version='.'.join(str(v) for v in VERSION),
    url='https://github.com/chaoooooo/gitcepter',
    packages=['gitcepter'],
    author='chao',
    author_email='qch5240@163.com',
    license='MIT',
    platforms='POSIX',
    description='Git interceptor to check commits and code style',
    long_description="",
    keywords=(
        'syntax-checker git git-hook python '
    ),
    entry_points={
        'console_scripts': [
            'gitcepter=gitcepter.gitcepter:main',
        ],
    },
)