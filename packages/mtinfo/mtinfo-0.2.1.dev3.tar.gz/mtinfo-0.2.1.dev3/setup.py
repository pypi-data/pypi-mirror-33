from setuptools import setup

from mtinfo import __version__ as version

setup(
    name = 'mtinfo',
    version = version,
    description = 'TVmaze/iMDB API Interface',
    long_description = 'TVmaze/iMDB API Interface',
    url = 'https://github.com/nixnodes/mtinfo',
    author = 'nixnodes',
    author_email = 'io@nixnodes.net',
    license = 'MIT',
    packages = [
        'mtinfo',
        'mtinfo.tvmaze',
        'mtinfo.tvmaze.tests'
    ],
    install_requires = [
        'requests',
    ],
    extras_require = {
        ':"linux" in sys_platform':  [
            "coloredlogs"
        ]
    },
    entry_points = {
        'console_scripts': [
            'tvmaze=mtinfo.tvmaze.main:main',
        ],
    },
    classifiers = (
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
