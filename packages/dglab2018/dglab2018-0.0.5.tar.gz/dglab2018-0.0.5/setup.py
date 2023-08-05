import setuptools
	  
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dglab2018",
    version="0.0.5",
    author="Dominik Gotojuch",
    author_email="dominik@gotojuch.com",
    description="Data processing and analysis scripts supporting the PhD project by one Dominik Gotojuch",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/robotgentleman/dglab2018",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)