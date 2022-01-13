from setuptools import setup
from glob import glob
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

exec(open('CorcLib/version.py').read())
current_setup = setup(
    name = "CorcLib",
    version = __version__,
    author = "Lucas Corcodilos",
    author_email = "corcodilos.lucas@gmail.com",
    description = "",
    license = "",
    keywords = "",
    url = "",
    packages = [], # A list of strings specifying the packages that setuptools will manipulate.
    scripts = [].extend(glob('scripts/')), # A list of strings specifying the standalone script files to be built and installed.
    install_requires = [], # A string or list of strings specifying what other distributions need to be installed when this one is. 
    long_description=read('README'),
)