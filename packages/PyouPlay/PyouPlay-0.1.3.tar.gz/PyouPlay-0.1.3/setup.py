from distutils.core import setup
from setuptools import setup


setup(
    name='PyouPlay',
    version='0.1.3',
    author="Omkar Yadav",
    author_email="omkar10859@gmail.com",
    packages=['PyouPlay'],
    install_requires=[
        "bs4>=0.0.1",
        "beautifulsoup4>=4.6.0",
        "requests>=2.19.1",
        "urllib3>=1.23",
        "certifi>=2018.4.16",
        "chardet>=3.0.4",
        "lxml>=4.2.3"
    ],
    scripts=['PyouPlay/get.py'],
    url="https://github.com/omi10859/PyouPlay",
    description="This is a simple python package when passed with a search argument, returns youtube video link.",
    long_description="A simple package to get youtube video links just by passing a search argument it can give a top one link and top 20 links.",

)
