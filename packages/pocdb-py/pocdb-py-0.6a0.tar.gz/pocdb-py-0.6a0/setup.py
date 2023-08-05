from setuptools import setup

setup(name='pocdb-py',
      version='0.6a',
      description='pocdb.com Python SDK',
      url='https://github.com/jeffthorne/pocdb-py',
      author='Jeff Thorne',
      author_email='jthorne@u.washington.edu',
      license='MIT',
      packages=['pocdb', 'pocdb.models', 'pocdb.utils'],
      install_requires=['requests'],
      zip_safe=False)



