"""
setup.py file for temperature module
"""


from setuptools import setup, find_packages

setup (name = 'temperature',
       version = '0.4',
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
	   packages = find_packages(),
	   package_data = {'temperature': ['*.h', '*.dll', '*.lib', '*.txt', '*.cxx']}
       )
