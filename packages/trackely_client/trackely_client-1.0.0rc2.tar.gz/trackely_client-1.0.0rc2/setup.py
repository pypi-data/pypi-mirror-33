from setuptools import setup
import trackely_client
import os

basepath = os.path.dirname(__file__)
binpath = os.path.join(basepath, 'bin')

setup(
  name = 'trackely_client',
  packages = ['trackely_client'],  
  long_description=open('README.md').read(),
  version = trackely_client.__version__,
  description = 'Client for trackely service',
  install_requires=['requests'],
  author = 'Gamaliel Espinoza',
  author_email = 'gamaliel.espinoza@gmail.com',
  url = 'https://github.com/gamikun/trackely-client-python',
  keywords = ['trackely'], 
  classifiers = [],
)