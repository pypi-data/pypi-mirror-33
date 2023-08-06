from setuptools import setup

setup(name='accoladecli', version='1.1', packages = ['cliparser'], author= 'J.V.', description= 'Accolade CLI'
      ,scripts=['cliparser/accolade'], install_requires= ['boto3'])
