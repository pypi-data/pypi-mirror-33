import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bethereum",
    version="0.0.0",
    author="Sebastian Fischer",
    author_email="python@bethereum.com",
    description="A python wrapper for the Bethereum SDK",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bethereum.com",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ),
)
