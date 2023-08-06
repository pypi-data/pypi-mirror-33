#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import re
from collections import OrderedDict

import setuptools

with io.open('README.md', 'rt', encoding='utf8') as f:
    readme = f.read()

with io.open('comment_fetcher/__init__.py', 'rt', encoding='utf8') as f:
    version = re.search(r'__version__ = \'(.*?)\'', f.read()).group(1)

setuptools.setup(
    name='CommentFetcher',
    version=version,
    url='https://github.com/lc-soft/CommentFetcher',
    license='MIT',
    author='Liu Chao',
    author_email='lc-soft@live.cn',
    maintainer='Liu Chao',
    maintainer_email='lc-soft@live.cn',
    description='A tool for collect code comments.',
    long_description=readme,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    zip_safe=False,
    platforms='any',
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries'
    ]
)
