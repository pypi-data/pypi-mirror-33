"""
setup.py file for motion module
"""

from distutils.core import setup, Extension
motion_module = Extension('_motion_2860', sources=['motion_2860_wrap.cxx'], library_dirs = ['.'], libraries = ['MPC2860'])

setup (name = 'motion_2860',
       version = '0.2',
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
       ext_modules = [motion_module],
       py_modules = ["motion_2860"],
	   data_files = [('description', ['MPC2860CFG.txt']),
					 ('head_files', ['motion_2860.h', 'MPC2860.h']),
					 ('libs', ['MPC2860.dll', 'MPC2860.lib'])
					 ]
       )
