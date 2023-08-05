from codecs import open
from setuptools import setup
from os import path

loc = path.abspath(path.dirname(__file__))

with open(path.join(loc, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(loc, 'musct', 'reference.py'), encoding='utf-8') as f:
    PROG_NAME = "unknown"
    VERSION = "unknown"
    exec(f.read())

setup(
    name=PROG_NAME,
    version=VERSION,
    description='Multiple user setting configuration tool',
    long_description=long_description,

    url='https://gitlab.com/xythrez/musct',
    author='Yiyao Yu',
    author_email='yuydevel@protonmail.com',

    keywords='rice settings config helper',
    classifiers=[
        'Operating System :: POSIX :: BSD',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
    ],

    packages=["musct", "musct.templates"],
    install_requires=[
        "pyyaml"
    ],
    entry_points="""
    [console_scripts]
    musct = musct.main:main
    """,
)
