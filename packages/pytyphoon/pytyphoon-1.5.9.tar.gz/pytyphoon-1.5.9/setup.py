from setuptools import setup, find_packages
from os.path import join, dirname
setup(
    name='pytyphoon',
    version='1.5.9',
    packages=find_packages(),
    include_package_data=True,
    author='The Typhoon Team',
    author_email='d.a.viharev@gmail.com',
    license="BSD",
    url="https://github.com/vortex14/typhoon",
    long_description=open(join(dirname(__file__), 'README.txt')).read(),
    install_requires=[
        'asyncio==3.4.3',
        'argparse==1.4.0',
        'tornado==4.5.3',
        'urllib3==1.22',
        'pynsq==0.8.2',
        'aioredis==1.1.0',
        'aiohttp==3.0.9',
        'python-socketio==1.9.0',
        'jsonschema==2.6.0',
        'requests==2.18.4',
        'watchdog==0.8.3'
    ]
)