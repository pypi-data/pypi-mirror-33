# -*- coding: utf-8 -
#
# This file is part of suds-passworddigest released under the MIT license. 
# See the NOTICE for more information.

import os
import sys
from setuptools import setup, find_packages

from suds_passworddigest import VERSION


setup(
    name='suds_passworddigest-homeassistant',
    version=VERSION+'dev0',
    description='adds Web Services Security'
                ' PasswordDigest authentication to SUDS',
    long_description='This package is created from https://github.com/tgaugry/suds-passworddigest-py3/archive/86fc50e39b4d2b8997481967d6a7fe1c57118999.zip#suds-passworddigest-py3==0.1.2a No updates are expected.',
    author='Victor Safronovich',
    author_email='vsafronovich@gmail.com',
    license='MIT',
    url='http://github.com/suvit/suds-passworddigest',
    zip_safe=False,
    packages=find_packages(exclude=['docs', 'examples', 'tests']),
    install_requires=['suds-py3'],
    include_package_data=True,
)
