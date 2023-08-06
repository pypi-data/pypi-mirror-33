from setuptools import setup
from petact import __version__

setup(
    name='petact',
    version=__version__,
    description='A package extraction tool',
    url='https://github.com/matthewscholefield/petact',
    author='Matthew Scholefield',
    author_email='matthew331199@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',

        'Topic :: System :: Filesystems',
        'Topic :: System :: Archiving :: Compression',
        'Topic :: Software Development :: Libraries :: Python Modules',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    keywords='tar extraction web download dependencies',
    packages=['petact'],
    install_requires=[],

    entry_points={
        'console_scripts': [
            'petact=petact.petact:main',
        ],
    }
)
