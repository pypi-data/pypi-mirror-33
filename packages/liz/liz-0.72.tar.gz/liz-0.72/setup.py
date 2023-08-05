from distutils.core import setup
setup(
  name = 'liz',
  packages = ['liz'],
  version = '0.72',
  description = 'A tool for creating websites',
  author = 'Alex Stachowiak',
  author_email = 'liz@stachowiak.email',
  url = 'https://github.com/stakodiak/liz', # use the URL to the github repo
  keywords = ['static', 'site', 'generator'],
  install_requres = ['jinja2'],
  entry_points={
    'console_scripts': [
      'liz = liz.main:main',
    ],
  },
)
