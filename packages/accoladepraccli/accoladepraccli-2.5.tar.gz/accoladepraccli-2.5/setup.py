from setuptools import setup

setup(name='accoladepraccli', version='2.5', packages = ['cliparser'], author= 'J.V.', description= 'Accolade CLI'
      ,scripts=['cliparser/accolade'], install_requires= ['boto3'])
