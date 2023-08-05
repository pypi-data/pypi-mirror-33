import setuptools
from distutils.core import setup

setup(
    name = 'UdicToolKits',
    #packages=['UdicToolKits'],
    #package_dir={'UdicToolKits':'TextPreprocessing'},
    #package_data={'UdicToolKits':['TextPreprocessing/*']},
    packages = setuptools.find_packages(),
    version = '1.05',
    description = 'udic dictionary, stopwords, TextPreprocessing module',
    author = ['yaochungfan'],
    author_email = 'yfan@nchu.edu.tw',
    url = 'https://github.com/UDICatNCHU/UdicToolKits',
    download_url = '',
    keywords = ['TextPreprocessing', 'dictionary', 'stopwords'],
    classifiers = [],
    license='GPL3.0',
)
