"""
setup.py file for motion module
"""

from setuptools import setup, find_packages

setup (name = 'motion_2860',
       version = '0.3',
       author = "SF Zhou WingC",
	   author_email = "1018957763@qq.com",
	   url = "https://github.com/KD-Group/motion_2860",
	   
	   license = 'GPL',
	   classifiers=[
		   'Development Status :: 3 - Alpha',
		   'Intended Audience :: Developers',
		   
		   'License :: OSI Approved :: GNU Affero General Public License v3',
		   'Programming Language :: Python :: 3',
		],
		
       description = "Python module for motion 2860",
	   packages = find_packages(),
	   package_data = {'motion_2860': ['*.h', '*.dll', '*.lib', '*.txt', '*.cxx']}
       )
