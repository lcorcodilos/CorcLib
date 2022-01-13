from setuptools import setup, find_packages
from glob import glob
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

exec(open('version.py').read())
current_setup = setup(
    name = "PACKAGE_NAME",
    version = __version__,
    author = "AUTHOR_NAME",
    author_email = "AUTHOR_EMAIL",
    description = "",
    license = "",
    keywords = "",
    url = "",
    packages = find_packages(),
    scripts = glob('scripts/*.py'), # A list of strings specifying the standalone script files to be built and installed.
    install_requires = [], # A string or list of strings specifying what other distributions need to be installed when this one is. 
    long_description=read('README.md'),
)