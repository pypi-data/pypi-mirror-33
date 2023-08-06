import os
from setuptools import setup

README = """
See the README on `GitHub
<https://github.com/uw-it-aca/uw-restclients-mailman>`_.
"""

# The VERSION file is created by travis-ci, based on the tag name
version_path = 'uw_mailman/VERSION'
VERSION = open(os.path.join(os.path.dirname(__file__), version_path)).read()
VERSION = VERSION.replace("\n", "")

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='UW-RestClients-Mailman',
    version=VERSION,
    packages=['uw_mailman'],
    author="UW-IT AXDD",
    author_email="aca-it@uw.edu",
    include_package_data=True,
    install_requires=['UW-RestClients-Core<1.0',
                      'UW-RestClients-SWS<2.0',
                      ],
    license='Apache License, Version 2.0',
    description=('A library for connecting to the mailman API'),
    long_description=README,
    url="https://github.com/uw-it-aca/uw-restclients-mailman",
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
    ],
)
