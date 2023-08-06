import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="moceansdk",
    version="0.1.1",
    author="Micro Ocean Technologies Sdn Bhd",
    author_email="support@moceanapi.com",
    description="Mocean SDK for Python",
    long_description="This is a Mocean SDK written in python, to use it you will need a mocean account. Signup for free at https://moceanapi.com",
    long_description_content_type="text/markdown",
    url="https://github.com/MoceanAPI/mocean-sdk-python",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python",
		"Programming Language :: Python :: 2",
		"Programming Language :: Python :: 2.7",
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3.4",
		"Programming Language :: Python :: 3.5",
		"Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)