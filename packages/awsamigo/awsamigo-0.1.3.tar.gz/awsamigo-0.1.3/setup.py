from distutils.core import setup

import awsamigo

version = awsamigo.__version__
author = awsamigo.__authors__[0].split('<')[0].strip()
author_email = awsamigo.__authors__[0].split('<')[1].strip()[:-1]

setup(
    name='awsamigo',
    version=version,
    author=author,
    author_email=author_email,
    packages=[
        'awsamigo',
    ],
    url='http://github.com/baccenfutter/awsamigo',
    license='LICENCE.txt',
    description="Wrapper for quick & easy AMI lookup via boto3.",
    long_description=open('README.rst').read(),
    keywords='tool development aws ami',
    python_requires='>=2.7',
    install_requires=[
        "boto3==1.7.52",
        "docopt==0.6.2",
    ],
    scripts=[
        'bin/awsamigo',
    ],
)
