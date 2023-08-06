import setuptools

setuptools.setup(
  name = 'evtxtoelk',
  version = '1.0.1',
  description = 'A lightweight tool to load Windows Event Log evtx files into Elasticsearch.',
  long_description = 'A lightweight tool to load Windows Event Log evtx files into Elasticsearch.',
  author = 'Dan Gunter',
  author_email = 'dangunter@gmail.com',
  url = 'https://github.com/dgunter/evtxtoelk',
  download_url = 'https://github.com/dgunter/evtxtoelk/archive/v1.0.0.tar.gz',
  packages = setuptools.find_packages(),
  keywords = ['InfoSec', 'Windows Event Logs', 'Elasticsearch', 'security'],
  install_requires=[
    "python-evtx",
    "elasticsearch",
    "xmltodict"
  ],
  classifiers=(
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Topic :: Security"
  ),
)
