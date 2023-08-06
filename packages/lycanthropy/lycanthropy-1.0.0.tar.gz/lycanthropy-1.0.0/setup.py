import versioneer
from setuptools import find_packages, setup
setup(
    name='lycanthropy',
    author='Robert Jordan',
    author_email='rojopolis@deba.cl',
    url='https://github.com/rojopolis/lycanthropy',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    packages=find_packages(),
)
