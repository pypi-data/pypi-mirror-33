import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="GC_analysis",
    version="0.3.1",
    author="Tony Yang",
    author_email="tony@tony.tc",
    description="A program that compute the GC percentage of a given genomic sequence",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tonyyzy/GC_analysis",
    packages=setuptools.find_packages(),
    scripts=['GC_analysis/GC_analysis.py'],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ),
)