from setuptools import setup 

with open("README.md", "r") as fh:
	long_discription = fh.read()

setup(name='cudamedfilt2d',
	version='1.0',
	description='A replacement for scipy.signal\'s medfilt2d() function using pycdua',
	url='https://github.com/Jackmastr/cudamedfilt2d',
	author='Jackson Sipple',
	packages=['cudamedfilt2d'],
	zip_safe=False)