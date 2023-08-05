import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="porter-stemmer-py",
    version="1.1.3",
    author="Binod Rai",
    author_email="binodrayee@gmail.com",
    description="Python implementation of Porter's stemming algorithm based on the original paper: http://tartarus.org/martin/PorterStemmer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/RaiBnod/porter-stemmer-py",
    packages=setuptools.find_packages(),
    license='Apache-2.0',
	classifiers=(
        "Programming Language :: Python",
        "Operating System :: OS Independent",
    ),
)
