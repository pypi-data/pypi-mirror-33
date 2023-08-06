import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="number_line",
    version="0.0.1",
    author="Liam McCluskey",
    author_email="lmm459@rutgers.edu",
    description="Package for creating a number line that contains different ranges and points",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/liammccluskey/number_line.git",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
		"Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
	py_modules=["number_line"]
)
