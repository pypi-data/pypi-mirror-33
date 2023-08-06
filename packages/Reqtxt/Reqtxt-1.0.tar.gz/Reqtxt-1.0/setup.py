import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Reqtxt",
    version="1.0",
    author="Labreche Abdellatif",
    author_email="abdellatif1898@gmail.com",
    description="Light weight third party package to generate the famous requirements.txt file",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/labTifo/reqtxt",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)