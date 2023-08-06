from setuptools import setup

import orchstr8

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='orchstr8',
    version=orchstr8.__version__,
    author='LBRY Inc.',
    author_email='hello@lbry.io',
    description='Services orchestration and testing library for torba and electrumx based projects.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/lbryio/orchstr8',
    license='MIT',
    keywords='bitcoin,torba,electrumx,lbry',
    classifiers=[
        'Framework :: AsyncIO',
        'Framework :: Twisted',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Topic :: Internet',
        'Topic :: Communications :: File Sharing',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Benchmark',
        'Topic :: System :: Distributed Computing',
        'Topic :: Utilities',
    ],
    packages=['orchstr8'],
    python_requires='>=3.6',
    install_requires=[
        'requests',
        'twisted'
    ],
    entry_points={
        'console_scripts': ['orchstr8=orchstr8.cli:main']
    },
)
