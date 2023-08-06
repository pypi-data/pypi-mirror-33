import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="findbyid",
    version="0.0.2",
    author="Kaappo Raivio",
    author_email="kaappo.raivio@gmail.com",
    description="A package that allows any instance of a class to be referenced with its ID that is provided by this package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/NoSocksForYou/findbyid.git",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)