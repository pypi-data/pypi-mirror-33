from setuptools import setup

setup(name='adjusty',
      version='1.1',
      description='A Simplified Python implementation of Adjust API for the KPI service',
      url='http://github.com/techieashish/adjusty',
      author='Ashish Srivastava',
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Programming Language :: Python :: 3'
      ],
      keywords='python adjust api nextadjust',
      author_email='ashisharivastava1872@gmail.com',
      packages=['adjusty'],
      install_requires=['requests'],
      zip_safe=False)