# University of Illinois at Urbana-Champaign
# The Whole Tale
# Summer Internship 2018
#
# Santiago Nunez-Corrales <nunezco2@illinois.edu>
# Copyright @ 2018, National Center for Supercomputing Applications. All rights reserved.
import setuptools


setuptools.setup(
    name='intros-MaxEnt',
    version='0.9.91',
    author='Santiago Nunez-Corrales',
    author_email='nunezco2@illinois.edu',
    packages=['introsmaxent'],
    url='https://wholetale.org',
    license='LICENSE.txt',
    description='A MaxEnt package with introspection for ecological niche modeling.',
    long_description=open('README.md').read(),
    python_requires='>3.4',
    install_requires=[
        'pandas >= 0.23.0',
        'requests >= 2.18',
        'basemap >= 1.1.0',
        'simplekml >= 1.2.8',
    ]
)
