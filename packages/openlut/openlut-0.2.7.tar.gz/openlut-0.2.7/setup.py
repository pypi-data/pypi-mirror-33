#!/usr/bin/env python3

# System
import os, sys

from os import path

from setuptools import setup, Extension, find_packages

path_setup = path.dirname(path.realpath(__file__))



# Extensions Handling
class PybindIncludes():
	"""
	Sneaky object that only imports pybind11 when it's becoming a string.
	
	This postpones the importing of pybind11 until after it's installed.
	
	Oh dynamic languages...
	"""

	def __init__(self, user=False):
		self.user = user

	def __str__(self):
		import pybind11
		return pybind11.get_include(user=self.user)

def get_ext_cpp() :
	# TODO: Allow bundling custom includes.	
	return [
		Extension(
			ext, # ext is a string denoting the python module path of the C++ source file.
			sources = [path.join(path_setup, ext.replace('.', os.sep) + '.cpp')],
			include_dirs=[PybindIncludes(), PybindIncludes(user=True)], #Includes as reported by Pybind11, and in the 'inc' directory.
			language = 'c++',
			extra_compile_args = ['-std=c++14', '-O3'],
			extra_link_args = ['-fopenmp']
		)
		for ext in ['openlut.lib.olOpt']
	]



# Setup Function
setup(	name = 'openlut',
		version = '0.2.7',
		description = 'OpenLUT is a practical color management library.',
		long_description = """# openlut - OSS tools for practical color management.

[![build status](https://git.sofusrose.com/so-rose/openlut/badges/master/build.svg)](https://git.sofusrose.com/so-rose/openlut/commits/master)

**Dev Repo** (Please submit Issues here): https://git.sofusrose.com/so-rose/openlut

**Mirror Repo**: https://www.github.com/so-rose/openlut

**PyPi Package**: https://pypi.python.org/pypi/openlut

What is it?
-----
openlut is a practical **color management library/tool** that aims to simplify and unify all the various methods of making accurate color transformations.

Supported transforms include:
* 1D and 3D LUTs
* Color Matrices
* Gamma Function
* CDL Transform

It's built on my own color pipeline needs - I needed a simple but close-to-the-math solutions that dealt not with images, but with float arrays.

As a tool, its main feature is that it's exceptionally easy to import, transform, and then save not only images, but also transforms.

Documentation
-----
Docs can be found at https://sofusrose.com/openlut. They're a work in progress for now (ColMap is 100% documented).

Installation
-----
0. **Check Versions**: Ensure you have Python 3.5+ installed.

1. **Get System Dependencies** - needing to do this is an unfortunate side effect of PyPi.
	* **On Debian/Ubuntu**: `sudo apt-get install python3-pip gcc libmagickwand-dev`
	* **On Mac**: `brew install python3 gcc imagemagick`

2. **Ensure Core Python Packages are Up To Date**: Simply run `pip3 install --user -U pip setuptools wheel` to do so.

2. **Install OpenLUT**: Run `pip3 install --user openlut`.
	* *This may take awhile, as it must compile the C++ Extension.*

Development
-----
1. **Clone the Repository**: This is easy enough to do - just run `git clone https://www.github.com/so-rose/openlut`.

2. **Compile Openlut**: Again, very easy - just run `./build <TARGET>`, where `<TARGET>` is some build target as listed in `./build -l`.

Troubleshooting
-----
**Pip doesn't work**: If Python is installed, but pip won't run, try running `curl https://bootstrap.pypa.io/get-pip.py | python3`

**Doesn't work on Windows**: I'm unsure of how pip compiles C Extensions on Windows, and have little willpower to investigate. If
you need Windows support, PM me and I'll see what I can do about it.

**Something's broken...**: There may be several bugs. If you start an Issue, then I can investigate.

I Want To Contribute!
------
Contributions are welcome! Let me know if you have any questions or issues.
""",
		long_description_content_type='text/markdown',
		
		author = 'Sofus Rose',
		author_email = 'sofus@sofusrose.com',
		url = 'https://www.github.com/so-rose/openlut',
		
		# ~ packages = ['openlut'], # Should match a symbolic link in this directory!
		packages = find_packages(), # Should find the package we need it to.
		
		ext_modules = get_ext_cpp(),

		license = 'MIT License',
		
		keywords = ['color', 'image', 'images', 'processing'],
		
		install_requires = ['pip', 'setuptools', 'wheel', 'virtualenv', 'twine', 'pybind11', 'sphinx', 'sphinx_rtd_theme', 'pyinstaller', 'numpy', 'pygame', 'PyOpenGL', 'scipy', 'Wand', 'setuptools', 'pybind11', 'wheel', 'setuptools', 'sphinx', 'sphinx_rtd_theme'],
		
		classifiers = ['Development Status :: 3 - Alpha', 'License :: OSI Approved :: MIT License', 'Operating System :: Unix', 'Operating System :: POSIX', 'Programming Language :: Python :: 3']
)
