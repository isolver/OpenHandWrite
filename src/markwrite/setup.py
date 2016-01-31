from setuptools import setup, find_packages

packages = find_packages()

from markwrite import __version__

setup(
      classifiers=[ #http://pypi.python.org/pypi?%3Aaction=list_classifiers
      'Development Status :: 3 - Alpha',
      'Environment :: Windows',
      'Intended Audience :: Science/Research',
      'License :: OSI Approved :: GNU General Public License (GPL)',
      'Operating System :: Microsoft :: Windows',
      'Programming Language :: Python',
      'Topic :: Scientific/Engineering',
      ],

    name='markwrite',
    version=__version__,
    packages=packages,
    package_data = {
        # If any package contains *.txt or *.rst files, include them:
        'markwrite': ['resources/icons/*.png','resources/tags/*.tag'],
        },
    url='https://github.com/isolver/OpenHandWrite#markwrite',
    license='GPL',
    author='Sol Simpson',
    author_email='sol@isolver-software.com',
    description='MarkWrite, part of the OpenHandWrite Project, is a tool for the inspection and segmentation of digitized writing data.'
)
