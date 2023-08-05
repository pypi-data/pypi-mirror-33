import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
	name = 'custom-sastrawi',
	version = '1.0.5',
	description = 'An indonesian text-mining library derived from PySastrawi (https://github.com/har07/PySastrawi) with certain modification',
	long_description=long_description,
	long_description_content_type="text/markdown",
	author = 'Yunaz Gilang',
	author_email = 'yunaz.gilang@gmail.com',
	url = 'https://github.com/YunazGilang/custom-sastrawi', # use the URL to the github repo
	keywords = ['sastrawi','custom','indonesian','text-mining'], # arbitrary keywords
	packages=setuptools.find_packages(),
	classifiers=(
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	),
	)