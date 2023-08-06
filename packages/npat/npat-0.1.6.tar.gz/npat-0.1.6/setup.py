from setuptools import setup, find_packages
setup(name='npat',
	  version='0.1.6',
	  description='Nuclear Physics Analysis Tools (NPAT) is a library written in python to assist in analysis of the physics of nuclear reactions and spectroscopy.',
	  url='https://github.com/jtmorrell/npat',
	  author='Jonathan Morrell',
	  author_email='jmorrell@berkeley.edu',
	  license='MIT',
	  packages=find_packages(),
	  include_package_data=True)
#, install_requires=['numpy>=1.11', 'matplotlib>=1.3', 'scipy>=0.19.1'])
