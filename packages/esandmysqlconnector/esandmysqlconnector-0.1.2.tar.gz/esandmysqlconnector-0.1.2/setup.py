import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="esandmysqlconnector",
    version="0.1.2",
    author="Coffeebeans",
    author_email="",
    description="A database setup for es and mysql clients",
    long_description=long_description,
    url="",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)