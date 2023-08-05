try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open("README.md", "r") as fh:
    long_description = fh.read()
    
setup(
  name = 'letolt',
  packages = ['letolt'],
  version = '0.2',
  description = 'Erettsegi letolto fuggveny 4 input alapjan.',
  long_description=long_description,
  long_description_content_type="text/markdown",
  author = 'Matyi',
  author_email = 'mmatyi1999@gmail.com',
  url = 'https://github.com/MatyiFKBT/letolt/',
  download_url = 'https://github.com/MatyiFKBT/letolt/archive/0.1.tar.gz',
  keywords = ['testing', 'erettsegi', 'letolt'],
  #packages=setuptools.find_packages(),
  classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
