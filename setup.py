from setuptools import setup, find_packages

setup(
    name="timetree_exporter",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'icalendar',
    ],
)
