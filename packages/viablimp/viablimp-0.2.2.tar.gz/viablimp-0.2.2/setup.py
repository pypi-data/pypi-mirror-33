from setuptools import setup,find_packages

def readme():
    with open('viablimp/README.rst') as f:
        return f.read()

setup(name='viablimp',
      version='0.2.2',
      description='logging messages by facebook bot to your account',
      long_description=readme(),
      url='https://facebooklogger.herokuapp.com/',
      author='Abhinav Rai',
      author_email='rai.1@iitj.ac.in',
      license='MIT',
      packages=['viablimp'],
      install_requires=[
        'requests'
		],
	classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Text Processing :: Linguistic',
        ],
      zip_safe=False)
