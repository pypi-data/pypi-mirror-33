from setuptools import setup, find_packages
import os
path = os.path.dirname(os.path.abspath(__file__))
print(path)
with open(os.path.join('README.rst'), encoding='utf-8') as f:
    long_desc = f.read()
setup(name="jhlangtool", 
	version="0.0.6", 
	author="Martin Vrbovčan",
	description="Program that converts jhipster language-specific JSON files into an excel file and back",
	packages=find_packages(), 
	long_description=long_desc,
	install_requires=['xlsxwriter>=1.0.3', 'pandas'],
	python_requires='>=3',
	entry_points = {
        'console_scripts': ['jhlangtool=jhlangtool:main'],
    },)