from setuptools import setup

exec(open('PACKAGE_NAME/version.py').read())
current_setup = setup(
    name = "PACKAGE_NAME",
    version = __version__,
    author = "AUTHOR_NAME",
    author_email = "AUTHOR_EMAIL",
    description = "",
    license = "",
    keywords = "",
    url = "",
    packages = [], # A list of strings specifying the packages that setuptools will manipulate.
    scripts = [] # A list of strings specifying the standalone script files to be built and installed.
    install_requires = [] # A string or list of strings specifying what other distributions need to be installed when this one is. 
    long_description=read('README.md'),
)