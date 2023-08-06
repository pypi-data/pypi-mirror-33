from setuptools import setup, find_packages

#python3 setup.py sdist bdist_wheel
#twine upload dist/blockcat-0.0.1*


VERSION = '0.3.4'

setup(name='blockcat',
      version=VERSION,
      description="a tiny blockchain explorer supporting different blockchains",
      long_description='just enjoy',
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='python blockchain exploerer Bitcoin terminal',
      author='mayotq',
      author_email='mayotq@gmail.com',
      url='https://github.com/mayotq/blockchain_explorer_clt',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=True,
      entry_points={
      'console_scripts':[
                         'blockcat = blockcat.input:main'
                         ]
      },
      )
