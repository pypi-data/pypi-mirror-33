# -*- encoding: UTF-8 -*-
from setuptools import setup, find_packages

"""
打包的用的setup必须引入，
"""

VERSION = '0.2.0'

setup(name='serviceultractl',
      version=VERSION,
      # package_data={'danmufm': ['template/*', ]},
      description="a tiny and smart cli player of dataultra based on Python",
      long_description='just enjoy',
      classifiers=[],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='python serviceultra su.cli terminal',
      author='su',
      author_email='du@huayun.com',
      url='http://demo.su.huayun.com/',
      license='MIT',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          'requests',
          'prettytable',
  	  'requests_toolbelt'
      ],
      entry_points={
          'console_scripts': [
              'suctl = serviceultractl.shell:main'
          ]
      },
      )
