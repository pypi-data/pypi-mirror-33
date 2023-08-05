import setuptools
from distutils.core import setup


with open('README.md','r') as f:
  readme = f.read()

setup(name='are_you_sure',
      version='1.0.2',
      description='Simple decorator to check before running',
      long_description=readme,
      long_description_content_type='text/markdown',
      author='Simon Ward-Jones',
      author_email='simonwardjones16@gmail.com',
      packages=['are_you_sure'],
      license='MIT',
      url='https://github.com/simonwardjones/are_you_sure',
      classifiers=['License :: OSI Approved :: MIT License',
                   'Programming Language :: Python :: 3',
                   'Programming Language :: Python']
      )
