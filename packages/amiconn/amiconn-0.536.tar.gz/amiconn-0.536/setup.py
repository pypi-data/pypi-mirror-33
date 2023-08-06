import sys
from distutils.core import setup
python_version = sys.version_info[:2]

if python_version < (2, 7):
    raise Exception("This version of xlrd requires Python 2.7 or above. ")

setup(name='amiconn',
      install_requires=['pyodbc','SQLAlchemy>=0.98'],
      author='QiQi',
      version='0.536',
      py_modules=['amiconn'],
    )
