import os, sys
from setuptools import setup, find_packages
from fnbr import __version__

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

requirements = []
with open('requirements.txt') as f:
  requirements = f.read().splitlines()

version = __version__
if not version:
    raise RuntimeError('version is not set')

setup(
    name="PyFNBR",
    version=version,
    author="JustMaffie",
    description="Python API wrapper for the FNBR.co API",
    long_description=open(os.path.join(os.path.dirname(__file__), "README.md")).read(),
    long_description_content_type='text/markdown',
    license="AGPL",
    keywords="API fortnite fnbr fnbr.co",
    packages=find_packages(),
    install_requires=requirements,
    url="https://github.com/JustMaffie/PyFNBR",
    project_urls={
        'Documentation': 'https://github.com/JustMaffie/PyFNBR/wiki',
        'Source': 'https://github.com/JustMaffie/PyFNBR'
    },
)