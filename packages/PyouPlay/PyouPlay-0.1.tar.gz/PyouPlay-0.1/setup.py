from setuptools import setup, find_packages
import PyouPlay.get

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='PyouPlay',
    version='0.1',
    author="Omkar Yadav",
    author_email="omkar10859@gmail.com",
    packages=['PyouPlay'],
    scripts=['PyouPlay/get.py'],
    url="https://github.com/omi10859/PyouPlay",
    description="This is a simple python package when passed with a search argument returns link to video.",
    long_description=long_description,
    install_requires=[
        "bs4>=0.0.1",
        "beautifulsoup4>=4.6.0",
        "requests>=2.19.1",
        "urllib3>=1.23",
        "certifi>=2018.4.16",
        "chardet>=3.0.4",
        "lxml>=4.2.3",
    ],
)
