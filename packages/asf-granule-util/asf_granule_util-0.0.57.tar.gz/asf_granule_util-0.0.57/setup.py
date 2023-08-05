
from setuptools import setup, find_packages

import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

long_description = '''
    Utility classes for making working with sential granule
    strings easier and more readable. Documentation can be found here:
    http://asf-granule-util-docs.s3-website-us-west-2.amazonaws.com/
'''

with codecs.open("version.txt", "r+") as f:
    version = f.read()


with codecs.open('requirements.txt', 'r') as f:
    requirements = f.read().strip().split('\n')[1:]

setup(
    name='asf_granule_util',
    version=str(version),

    description='Library for handling sential granules',
    long_description=long_description,

    url='https://github.com/asfadmin/hyp3-time-series-lib',

    author='ASF Student Development Team 2017',
    author_email='eng.accts@asf.alaska.edu',

    license="'License :: OSI Approved :: MIT License'",

    classifiers=['Development Status :: 3 - Alpha',

                 # Indicate who your project is intended for
                 'Intended Audience :: Science/Research',
                 'Topic :: Scientific/Engineering :: GIS',

                 # Specify the Python versions you support here. In particular, ensure
                 # that you indicate whether you support Python 2, Python 3 or both.
                 'Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3',
                 ],
    keywords='granule asf sential util',
    packages=find_packages(),
    install_requires=requirements

)
