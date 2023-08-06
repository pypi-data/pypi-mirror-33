import setuptools

with open("README.md", "r") as f:
	long_description = f.read()

setuptools.setup(name = "dipswitch",
	version = "1.0",
	author = "Declan Hoare",
	author_email = "declanhoare@exemail.com.au",
	description = "Switch statements for Python",
	long_description = long_description,
	long_description_content_type = "text/markdown",
	url = "https://home.exetel.com.au/declanhoare/projects/dipswitch.git",
	packages = setuptools.find_packages(),
	classifiers = ("Programming Language :: Python :: 3",
		"License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
		"Operating System :: OS Independent"))

