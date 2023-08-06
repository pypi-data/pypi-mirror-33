#!/usr/bin/env python3

#from distutils.core import setup
import platform
import setuptools

def build_params():
    params = {
      'name':'copycat-clipboard3',
      'version':'1.0',
      'description':'easy way let use clip on command line with system clip (support python 3)',
      'author':'Ming',
      'author_email':'ming@alone.tw',
      'url':'https://github.com/iwdmb/copycat',
      'py_modules':['copycat3'],
	  'license':'MIT',
      'install_requires': ['clime', 'pyclip-copycat'],
    }
    if platform.system() == 'Windows':
        params['scripts'] = ['copycat3.bat']
    else:
        params['scripts'] = ['copycat3']

    return params

setuptools.setup (
    **build_params()
)
