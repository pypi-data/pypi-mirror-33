"""
setup.py file for temperature module
"""

from distutils.core import setup, Extension
temperature_module = Extension('_temperature', sources=['temp_wrap.cxx'], library_dirs = ['.'], libraries = ['Temperature'])

setup (name = 'temperature',
       version = '0.1',
       author = "SF Zhou WingC",
	   author_email = "1018957763@qq.com",
	   url = "https://github.com/KD-Group/temperature",
	   
	   license = 'GPL',
	   classifiers=[
		   'Development Status :: 3 - Alpha',
		   'Intended Audience :: Developers',
		   
		   'License :: OSI Approved :: GNU Affero General Public License v3',
		   'Programming Language :: Python :: 3',
		],
		
       description = "Python module for temperature",
       ext_modules = [temperature_module],
       py_modules = ["temperature"],
	   data_files = [('head_files', ['temp.h', 'Temperature.h']),
					 ('libs', ['Temperature.dll', 'Temperature.lib'])
					 ]
       )
