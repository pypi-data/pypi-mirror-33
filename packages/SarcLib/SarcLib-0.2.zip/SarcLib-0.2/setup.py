from setuptools import setup

setup(
    name = 'SarcLib',
    packages = ['SarcLib'],
    version = '0.2',
    description = 'A library for handling the Nintendo SARC archive format',
    author = 'AboodXD',
    author_email = 'aboood40091@gmail.com',
    url = 'https://github.com/aboood40091/SarcLib',
    download_url = 'https://github.com/aboood40091/SarcLib/archive/v0.2.tar.gz',
    keywords = ['arc', 'sarc', 'szs'],
    license = 'GNU General Public License v3 (GPLv3)',
    classifiers = [
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Archiving',
    ],
)
