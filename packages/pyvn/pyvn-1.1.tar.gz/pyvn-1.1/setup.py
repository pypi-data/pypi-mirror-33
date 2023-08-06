#!/usr/bin/env python3

from setuptools import setup

setup(
	name="pyvn",
	version='1.1',
	description='Python3 Ivnosys Utils',
	author='Ivnosys Soluciones S.L.',
	author_email='jbiosca@ivnosys.com',
	url='https://ivnosys.com',
	python_requres='>=3.5',
	#packages=["lib"],
	packages=["pyvn"],
	package_dir={"pyvn": "src"},
	#py_modules=['ivscript', 'jdata', 'josen', 'run']
	install_requires=[
		'setuptools',
		'dicttoxml',
		'xmltodict',
		'ruamel.yaml',
	],
	classifiers=[
		# 5 - Production/Stable
		'Development Status :: 4 - Beta',
		#'Topic :: Software development',
	],

)
