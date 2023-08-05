from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
  long_description = f.read()

setup(
  name='dt_send_answers',
  version='0.1.3',
  description='Code to help Docassemble Toolkit users store answers to their interviews',
  url='https://github.com/communitylawyer/dt_send_answers',
  author='Community.lawyer, PBC',
  author_email='hello@community.lawyer',
  license='MIT',
  py_modules=['dt_send_answers']
)