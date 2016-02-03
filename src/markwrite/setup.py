from setuptools import setup, find_packages

packages = find_packages()

from markwrite import __version__

setup(
      classifiers=[ #http://pypi.python.org/pypi?%3Aaction=list_classifiers
      'Development Status :: 4 - Beta',
      'Environment :: Win32 (MS Windows)',
      'Intended Audience :: Science/Research',
      'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
      'Operating System :: Microsoft :: Windows',
      'Natural Language :: English'
      'Programming Language :: Python :: 2.7',
      'Programming Language :: Python :: Implementation :: CPython',
      'Topic :: Scientific/Engineering',
      'Topic :: Software Development :: Libraries :: Python Modules'
      ],

    name='markwrite',
    version=__version__,
    packages=packages,
    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        'markwrite': ['resources/icons/*.png','resources/tags/*.tag'],
        },
    url='https://github.com/isolver/OpenHandWrite#markwrite',
    license='GPLv3+',
    author='Sol Simpson',
    author_email='sol@isolver-software.com',
    description='MarkWrite, part of the OpenHandWrite Project, is a tool for the inspection and segmentation of digitized writing data.'
)
