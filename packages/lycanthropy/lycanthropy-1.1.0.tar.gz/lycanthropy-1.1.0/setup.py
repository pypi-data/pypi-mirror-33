from os import path
import versioneer
from setuptools import find_packages, setup


this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md')) as f:
    long_description = f.read()

setup(
    name='lycanthropy',
    author='Robert Jordan',
    author_email='rojopolis@deba.cl',
    url='https://github.com/rojopolis/lycanthropy',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(),
    long_description=long_description,
    long_description_content_type='text/markdown'
)
