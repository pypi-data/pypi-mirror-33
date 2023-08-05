import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ElexonAPIWrapper",
    version="0.0.2",
    author="Ayrton Bourn",
    author_email="AyrtonBourn@Outlook.com",
    description="A package to aid with the retrieval of data from the freely available Elexon available ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/ElexonAPIWrapper",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)