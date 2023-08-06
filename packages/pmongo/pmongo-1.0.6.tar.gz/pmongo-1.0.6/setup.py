from distutils.core import setup
import os, io

from pmongo import __version__

here = os.path.abspath(os.path.dirname(__file__))
README = io.open(os.path.join(here, 'README.md'), encoding='UTF-8').read()
CHANGES = io.open(os.path.join(here, 'CHANGES.md'), encoding='UTF-8').read()
setup(name="pmongo",
      version=__version__,
      keywords=('mongo', 'django', 'orm', 'nosql'),
      description="A small Python MongoDB Document-Based access engine.",
      long_description=README + '\n\n\n' + CHANGES,
      url='https://github.com/sintrb/pmongo/',
      author="trb",
      author_email="sintrb@gmail.com",
      packages=['pmongo'],
      install_requires=['pymongo'],
      zip_safe=False
      )
