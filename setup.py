try:
    from setuptools import setup
    import setuptools
except ImportError:
    raise ImportError(
        "setuptools module required, please go to "
        "https://pypi.python.org/pypi/setuptools and follow the instructions "
        "for installing setuptools"
    )
from codecs import open
from os import path
import sys

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

INSTALL_REQUIRES = ['apache-libcloud>=2.0.0',
                    'blessed>=1.14.2',
                    'colorama>=0.3.9',
                    'configparser>=3.5.0',
                    'future>=0.14',
                    'gevent>=1.2.2',
                    'pycrypto>=2.6.1',
                    'PrettyTable>=0.7.2']

EXTRAS_REQUIRE = {
    ":python_full_version<'2.7.9'": [
        "requests >=2.5.1, <=2.7.0",
        "certifi <= 2015.9.6.2",
        "pyOpenSSL>=17.0.0",
        "lxml>=3.8",
        "cssselect>=1.0.1",
        "ndg-httpsclient>=0.4.0",
        "pyasn1>=0.2.3",
        "backports.ssl_match_hostname>=3.5.0"
    ],
    ":python_full_version>='2.7.9'": [
        "requests >= 2.5.1"
    ]
}

if int(setuptools.__version__.split(".", 1)[0]) < 18:
    assert "bdist_wheel" not in sys.argv, "setuptools 18 required for wheels."
    # For legacy setuptools + sdist.
    if sys.version_info[0:3] <= (2, 7, 8):
        INSTALL_REQUIRES.append("requests >=2.5.1, <=2.7.0")
        INSTALL_REQUIRES.append("certifi <= 2015.9.6.2")
        INSTALL_REQUIRES.append("pyOpenSSL>=17.0.0")
        INSTALL_REQUIRES.append("lxml>=3.8")
        INSTALL_REQUIRES.append("cssselect>=1.0.1")
        INSTALL_REQUIRES.append("ndg-httpsclient>=0.4.0")
        INSTALL_REQUIRES.append("pyasn1>=0.2.3")
        INSTALL_REQUIRES.append("backports.ssl_match_hostname>=3.5.0")
        EXTRAS_REQUIRE = {}
    else:
        INSTALL_REQUIRES.append("requests >= 2.5.1")

setup(
    name='mcc',
    packages=['mcc'],
    package_data={'mcc': ['config.ini']},
    entry_points={'console_scripts': ['mcc=mcc.core:main',
                                      'mccl=mcc.core:list_only']},
    version='0.9.1',
    author="Robert Peteuil",
    author_email="robert.s.peteuil@gmail.com",
    url='https://github.com/robertpeteuil/multi-cloud-control',
    download_url='https://pypi.python.org/pypi/mcc',
    license='GNU General Public License v3 (GPLv3)',
    description='Unified Instance Management Utility across AWS, Azure and GCP Platforms',
    keywords='aws-ec2 gcp-compute azure-vm utility control ssh start stop connect',
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
    classifiers=[
        'Development Status :: 4 - Beta',
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
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: System :: Distributed Computing',
        'Topic :: System :: Systems Administration'],
    long_description=long_description

)
