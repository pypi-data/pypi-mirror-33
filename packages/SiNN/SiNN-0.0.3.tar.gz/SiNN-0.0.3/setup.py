import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="SiNN",
    version="0.0.3",
    author="SiCNN Author",
    author_email="lincolnauster@gmail.com",
    description="A simple way to make neural nets: Machine learning without linear algebra",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pithonmath/neuralnet",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
