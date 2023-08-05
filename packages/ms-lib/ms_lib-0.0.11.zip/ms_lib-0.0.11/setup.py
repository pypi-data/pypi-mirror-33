from distutils.core import setup
setup(
  name = 'ms_lib',
  package_dir={
    'ms_lib': 'ms_lib',
    'ms_lib.storage': 'ms_lib/storage'},
  packages=['ms_lib', 'ms_lib.storage'], # this must be the same as the name above
  version = '0.0.11',
  description = 'This is the microservices library developed by eHealthz group.',
  author = 'Jorge Sancho',
  author_email = 'jslarraz@gmail.com',
  url = 'https://github.com/jslarraz/ms_lib', # use the URL to the github repo
  download_url = 'https://github.com/jslarraz/ms_lib/tarball/0.1',
  keywords = ['microservices', 'development'],
  install_requires=[
    'flask', 'jsonschema', 'bson', 'pymongo',
  ],
  classifiers = [],
)
