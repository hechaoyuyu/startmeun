__author__="hechao"
__date__ ="$2011-3-31 17:46:46$"

from setuptools import setup,find_packages

setup (
  name = 'ymenu',
  version = '2.9',
  packages = find_packages(),

  # Declare your packages' dependencies here, for eg:
  install_requires=['foo>=3'],

  # Fill in these to make your Egg ready for upload to
  # PyPI
  author = 'hechao',
  author_email = 'hechao@115.com',

  url = 'www.ylmf.org',
  license = 'GPL v3',
  long_description= 'Ylmf OS Menu',
)