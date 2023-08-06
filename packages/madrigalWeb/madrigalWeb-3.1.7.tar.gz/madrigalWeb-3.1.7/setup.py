"""set up file for the Python Madrigal Remote API

$Id: setup.py 6520 2018-06-26 20:04:10Z brideout $
"""
import os, os.path, sys

from distutils.core import setup
    
setup(name="madrigalWeb",
      version="3.1.7",
      description="Remote Madrigal Python API",
      author="Bill Rideout",
      author_email="brideout@haystack.mit.edu",
      url="http://cedar.openmadrigal.org",
      packages=["madrigalWeb"],
      keywords = ['Madrigal'],
      scripts=['madrigalWeb/globalIsprint.py', 'madrigalWeb/globalDownload.py',
               'madrigalWeb/examples/exampleMadrigalWebServices.py']
      )

    