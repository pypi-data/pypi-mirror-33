#-----------------------------------------------------------------------------
# Name:        setup
# Purpose:    
# Author:      Aric Sanders
# Created:     12/30/2017
# License:     MIT License
#-----------------------------------------------------------------------------
""" Module for distribution """
#-----------------------------------------------------------------------------
# Standard Imports
from setuptools import setup, find_packages

#-----------------------------------------------------------------------------
# Third Party Imports

#-----------------------------------------------------------------------------
# Module Constants

#-----------------------------------------------------------------------------
# Module Functions

#-----------------------------------------------------------------------------
# Module Classes

#-----------------------------------------------------------------------------
# Module Scripts

#-----------------------------------------------------------------------------
# Module Runner
if __name__ == '__main__':


    setup(
        name='pyMez',
		
		package_dir={'':'src'} ,
        packages=find_packages('src'),  # this must be the same as the name above
		#include_package_data=True,
		package_data = {'': ['*.txt', '*.xml', '*.html', '*.ipynb','*.xsl'],},
        version='0.3.01',
        description='Measurement, Analysis and Data Management Software. To load the API interface use from pyMez import *.',
		long_description="""pyMez is a python package born out of the daily needs of a laboratory scientist. In particular, there is a constant need to use external equipment to acquire data, store that data in a sensible way, analyze the stored data, and generate collections and reports after analyzing the data. In the world of scientific computation there is an endless universe of solutions to do this, however none of the solutions met my personal daily needs and philosophy simultaneously. This package tries to stitch together many tools to meet those needs, while serving as a backend library to a webserver. It thus has many dependencies. Some of the dependencies are os specific, however the lack of them should not prevent operation. Although it currently has a single primary developer, it is my hope that it will be adopted by at least 10's of people and help them accomplish their daily scientific goals.""",
        author='Aric Sanders',
        author_email='aric.sanders@gmail.com',
        url='https://github.com/aricsanders/pyMez',  # use the URL to the github repo
        download_url='https://github.com/aricsanders/pyMez.git',  # I'll explain this in a second
        keywords=['measurement', 'data handling', 'example'],  # arbitrary keywords
        classifiers=['Programming Language :: Python :: 2.7'],
		license="MIT",
		install_requires=['markdown','numpy','pandas',"Pillow","pdfkit",
		"pdoc","networkx","pyvisa","scipy","matplotlib","pythonnet","pywin32"],
    )
    