"""
setup.py file for temperature module
"""


import distutils.sysconfig
from distutils.core import setup, Extension
temperature_module = Extension('_temperature', sources=['temp_wrap.cxx'], library_dirs = ['.'], libraries = ['Temperature'])

setup (name = 'temperature',
       version = '0.3',
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
	   data_files = [(distutils.sysconfig.get_python_lib(), ['temp.h', 'Temperature.h', 
															 'Temperature.dll', 'Temperature.lib'])
					]
       )
