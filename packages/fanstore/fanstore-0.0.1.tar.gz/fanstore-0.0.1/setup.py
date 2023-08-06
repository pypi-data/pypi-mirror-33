import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fanstore",
    version="0.0.1",
    author="Zhao Zhang, Lei Huang, Niall Gaffney",
    author_email="zzhang@tacc.utexas.edu",
    description="Fanstore gathers local storage space in computer clusters to enable distirbuted neural networks training with larger datasets",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zhaozhang/fanstore",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
