import glob
from distutils.core import setup

from setuptools import find_packages

NAME = "webgather"
# scripts = glob.glob("bin/webgather")
setup(name='webgather',
      url="http://47.100.219.148:10000/basin/basin-webgather",
      author="chenqian",
      author_email='7671557@qq.com',
      download_url='http://47.100.219.148:10000/basin/basin-webgather',
      include_package_data=True,
      keywords=['command', 'line', 'tool'],
      packages=find_packages(),
      version='0.2',
      install_requires=["requests", "pyquery"],
      py_modules=['webgather','fetcher_manager', 'page_parse', 'page_list_url_checker'],
      )
