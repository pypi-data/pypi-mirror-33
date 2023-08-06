import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
	name='ocldev',
    version='0.0.1',
	author='Open Concept Lab',
	author_email='info@openconceptlab.org',
	description='Development library for working with OCL metadata and APIs',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='http://github.com/OpenConceptLab/ocldev',
	packages=setuptools.find_packages(),
	license='MPL2.0',
	classifiers=(
		"Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
        "Operating System :: OS Independent",
	)
)
