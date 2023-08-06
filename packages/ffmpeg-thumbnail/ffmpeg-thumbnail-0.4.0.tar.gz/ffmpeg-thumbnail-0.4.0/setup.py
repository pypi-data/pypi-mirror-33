import re
import os.path
from setuptools import setup, find_packages

# reading package's version
with open(os.path.join(os.path.dirname(__file__), 'ffmpeg_thumbnail', '__init__.py')) as v_file:
    package_version = re.compile(r".*__version__ = '(.*?)'", re.S).match(v_file.read()).group(1)

setup(
    name='ffmpeg-thumbnail',
    version=package_version,
    author='Mahdi Ghane.g',
    zip_safe=False,
    include_package_data=True,
    packages=find_packages()
)
