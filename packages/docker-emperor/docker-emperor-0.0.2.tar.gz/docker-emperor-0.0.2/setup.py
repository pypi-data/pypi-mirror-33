import os
import setuptools


def find_version(*parts):
    from docker_emperor.version import __version__
    return "{}".format(__version__)

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setuptools.setup(
    name='docker-emperor',
    version=find_version(),
    author = "Damien Autrusseau",
    author_email = "damien.autrusseau@gmail.com",
    description = ("Docker CLI that combine compose and machine for a full stack deployment"),
    license = "Apache Software License",
    keywords = "",
    url = "https://pypi.org/project/docker-emperor",
    #packages=['tests'],
    long_description=read('README.rst'),
    packages=setuptools.find_packages(exclude=('tests',)),
    install_requires=[
        'PyYAML==3.12',
        'six==1.11.0',
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    entry_points = {
        'console_scripts': [
            'docker-emperor = docker_emperor:entrypoint',    
            'de = docker_emperor:entrypoint',                
        ],              
    },
)