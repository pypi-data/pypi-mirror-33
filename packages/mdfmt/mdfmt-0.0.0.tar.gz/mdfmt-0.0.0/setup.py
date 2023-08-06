#!/usr/bin/env python

from setuptools import setup, find_packages

__version__ = '0.0.0'
__program__ = 'mdfmt'

long_description = \
'''

'''

setup(
    name=__program__,
    version=__version__,
    description='Markdown formatter',
    long_description=long_description,
    keywords="markdown formatter",
    author='Noel Martignoni',
    author_email='noel@martignoni.fr',
    url='http://gitlab.com/xneomac/mdfmt',
    scripts=['{}'.format(__program__)],
    install_requires=['mistune'],
    packages=find_packages(exclude=['tests*']),
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Topic :: Utilities']
)
