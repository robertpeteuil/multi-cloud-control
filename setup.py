try:
    from setuptools import setup
except ImportError:
    raise ImportError(
        "setuptools module required, please go to "
        "https://pypi.python.org/pypi/setuptools and follow the instructions "
        "for installing setuptools"
    )
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='mcc',
    packages=['mcc'],
    package_data={'mcc': ['config.ini']},
    entry_points={'console_scripts': ['mcc=mcc.core:main']},
    version='0.0.10',
    author="Robert Peteuil",
    author_email="robert.s.peteuil@gmail.com",
    url='https://github.com/robertpeteuil/aws-shortcuts',
    license='GNU General Public License v3 (GPLv3)',
    description='Unified CLI Utility for AWS, Azure and GCP Instance Control',
    platforms='any',
    keywords='Unified Cloud Utility Instance AWS EC2 Azure GCP Multi-Provider',
    install_requires=['apache-libcloud',
                      'PyCrypto',
                      'prettytable',
                      'configparser',
                      'colorama'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: System :: Distributed Computing',
        'Topic :: System :: Systems Administration'],
    long_description=long_description

)
