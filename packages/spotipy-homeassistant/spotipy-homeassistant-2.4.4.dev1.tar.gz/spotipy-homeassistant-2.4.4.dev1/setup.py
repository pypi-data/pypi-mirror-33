from setuptools import setup

setup(
    name='spotipy-homeassistant',
    version='2.4.4.dev1',
    description='simple client for the Spotify Web API',
    long_description='This package is created from https://github.com/happyleavesaoc/spotipy/archive/544614f4b1d508201d363e84e871f86c90aa26b2.zip#spotipy==2.4.4 No updates are expected.',
    author="@plamere",
    author_email="paul@echonest.com",
    url='http://spotipy.readthedocs.org/',
    install_requires=[
        'requests>=2.3.0',
        'six>=1.10.0',
    ],
    license='LICENSE.txt',
    packages=['spotipy'])
