import codecs
import os
import sys
# 坚实的附近发生
try:

    from setuptools import setup

except:

    from distutils.core import setup

def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()

 

NAME = "pypi_wenyali_test"


PACKAGES = ['wenyali','wyl']


DESCRIPTION = "this is a test package for return hello world"


LONG_DESCRIPTION = "import index function return hello world"


KEYWORDS = "hello world"
 

AUTHOR = "wenyali"


AUTHOR_EMAIL = "2917073217@qq.com"


URL = "https://github.com/lichanghong/wenyali.git"



VERSION = "1.1.2"



LICENSE = "MIT"



setup(

    name =NAME,version = VERSION,description = DESCRIPTION,long_description =LONG_DESCRIPTION,

    classifiers =[

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python',

        'Intended Audience :: Developers',

        'Operating System :: OS Independent',

    ],

      keywords =KEYWORDS,author = AUTHOR,author_email = AUTHOR_EMAIL,url = URL, packages = PACKAGES,include_package_data=True,zip_safe=True,
      entry_points={
      "console_scripts": [
                          "pypi_wenyali_test = wenyali.index:index",
                          ]
      },

)
