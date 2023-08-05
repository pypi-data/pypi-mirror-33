from distutils.core import setup
setup(
  name          = 'py3awstoolbox',
  packages      = ['py3awstoolbox'],
  version       = '0.0.7',
  description   = 'A Python3 AWS tools and utilities collection',
  author        = 'Fan Yang',
  author_email  = 'gr82morozr@gmail.com',
  url           = 'https://gr82morozr@bitbucket.org/gr82morozr/py3-awstoolbox.git',  
  download_url  = 'https://gr82morozr@bitbucket.org/gr82morozr/py3-awstoolbox.git', 
  keywords      = ['Utility', 'Tools' ], 
  classifiers   = [],
  install_requires=['boto3']
)
