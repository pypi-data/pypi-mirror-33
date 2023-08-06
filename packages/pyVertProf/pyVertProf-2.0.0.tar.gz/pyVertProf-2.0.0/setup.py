######!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

# Import of the lib pyVertProf
import pyVertProf

def readme():
	with open('README.rst') as f:
		return f.read()

setup(name='pyVertProf',
	#version='0.1.1',
	version=pyVertProf.__version__,
	description='package that provide tools to perform stats on vertical profils',
	long_descritpion=open('README.rst').read(),
	url='https://github.com/robertxa/pyVertProf',
	download_url='https://github.com/robertxa/pyVertProf/archive/master.zip',
	author='Xavier Robert',
	author_email='xavier.robert@univ-grenoble-alpes.fr',
	license='CCby-nc-sa',
	packages=find_packages(),
	install_requires=[
	      'kapteyn'
	],
	classifiers=[
		#"Programming language :: Python",
		"Operating System :: OS Independent",
		#"Programming Language :: Python :: 3",
		"Topic :: Scientific/Engineering :: Visualization"
	#	"Topic :: Scientific/Engineering :: GIS"
	],
	include_package_data=True,
	zip_safe=False)
      