import setuptools

setuptools.setup(
  name = 'parsebrologs',
  version = '1.1.4',
  description = 'A lightweight utility for programmatically reading and manipulating Bro IDS log files and outputting into JSON or CSV format.',
  long_description = 'A lightweight utility for programmatically reading and manipulating Bro IDS log files and outputting into JSON or CSV format.',
  author = 'Dan Gunter',
  author_email = 'dangunter@gmail.com',
  url = 'https://github.com/dgunter/parsebrologs',
  download_url = 'https://github.com/dgunter/ParseBroLogs/archive/v1.1.4.tar.gz',
  packages = setuptools.find_packages(),
  keywords = ['InfoSec', 'Bro IDS', 'security'],
  classifiers=(
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Topic :: Security"
  ),
)