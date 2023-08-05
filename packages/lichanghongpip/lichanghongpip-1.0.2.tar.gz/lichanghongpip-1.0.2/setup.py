import codecs
import os
import sys


try:

    from setuptools import setup

except:

    from distutils.core import setup

def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()

 

NAME = "lichanghongpip"


PACKAGES = ['sourceforprint',]


DESCRIPTION = "this is a test package return a number"


LONG_DESCRIPTION = "import index function return a number"


KEYWORDS = "number"
 

AUTHOR = "wenyali"


AUTHOR_EMAIL = "2917073217@qq.com"


URL = "https://github.com/lichanghong/wenyali.git"



VERSION = "1.0.2"



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

)
