from distutils.core import setup


version = "0.1.5"
setup(
    name='awsamigo',
    version=version,
    author='Brian Wiborg',
    author_email='baccenfutter@c-base.org',
    packages=['awsamigo'],
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
    extras_require={
        'dev': [
            "twine==1.11.0",
        ],
    },
    scripts=[
        'bin/awsamigo',
    ],
)
