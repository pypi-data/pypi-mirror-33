from setuptools import setup,find_packages

def readme():
    with open('viablimp/README.rst') as f:
        return f.read()

setup(name='viablimp',
      version='0.1',
      description='logging messages by facebook bot to your account',
      long_description=readme(),
      url='http://github.com/theflyingmantis/facebooklogger',
      author='Abhinav Rai',
      author_email='rai.1@iitj.ac.in',
      license='MIT',
      packages=['viablimp'],
      install_requires=[
        'requests'
		],
      zip_safe=False)
