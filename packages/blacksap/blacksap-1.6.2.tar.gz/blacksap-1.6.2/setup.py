#!/usr/bin/env python
# coding=utf-8
"""Setup script for blacksap project"""

from setuptools import setup

setup(name='blacksap',
      version='1.6.2',
      description='Track torrent RSS feeds',
      author='Jesse Almanrode',
      author_email='jesse@almanrode.com',
      url='https://bitbucket.org/isaiah1112/blacksap',
      py_modules=['blacksap'],
      license='GNU General Public License v3 or later (GPLv3+)',
      install_requires=['click==6.7',
                        'colorama==0.3.9',
                        'feedparser==5.2.1',
                        'PySocks==1.6.8',
                        'requests==2.19.1',
                        ],
      platforms=['Linux',
                 'Darwin',
                 ],
      entry_points="""
            [console_scripts]
            blacksap=blacksap:cli
      """,
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: End Users/Desktop',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Natural Language :: English',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: POSIX :: Linux',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: Implementation :: CPython',
          'Programming Language :: Python :: Implementation :: PyPy',
          'Topic :: Communications :: File Sharing',
          'Topic :: Utilities',
          ],
      )
