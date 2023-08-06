from setuptools import setup

setup(name='accoladepraccli', version='2.0', packages = ['cliparser'], author= 'J.V.', description= 'Accolade CLI'
      ,scripts=['cliparser/sa.py'], install_requires= ['boto3'])
