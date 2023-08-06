# -*- encoding: UTF-8 -*-
from setuptools import setup, find_packages

VERSION = "0.1.5"

setup(name='kg_downloader',
      version=VERSION,
      description="a python tool which download songs from kg.qq.com.",
      long_description="This is a sexy tool that help you download songs from kg.qq.com(`全民K歌` in Chinese).There're two different types of urls, one is the song playing page, the other is the songer page.\nIf you give the song playing page's url. Kg_downloader will download the playing song on the page as you wish. However if you give the singer page's url, The **whole** songs that this singer published will be downloaded.Of course you can choose where to put this downloaded items, just use the `-l|--location`.",
      classifiers=[
          "Development Status :: 5 - Production/Stable",
          "Operating System :: OS Independent",
          "Programming Language :: Python :: 3 :: Only",
          "Topic :: Terminals"
      ],  # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='python3 terminal downloader',
      author='justin13',
      author_email='justin13wyx@gmail.com',
      url="https://github.com/Justin13wyx/Python_Tools",
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'requests',
          'lxml'
      ],
      entry_points={
          'console_scripts': [
              'kg_downloader = kg_downloader.main:main'
          ]
      },
      )
