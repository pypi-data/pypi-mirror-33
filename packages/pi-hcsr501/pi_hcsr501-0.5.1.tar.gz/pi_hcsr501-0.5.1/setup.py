#!/usr/bin/env python3

import setuptools

with open("README.md", "r") as f:
	long_description = f.read()

setuptools.setup(
	name='pi_hcsr501',
	version='0.5.1',
	author='Toni Kangas',
	description='Library to read hcsr501 sensor.',
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/kangasta/pi_hcsr501",
	packages=setuptools.find_packages(),
	classifiers=(
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	)
)