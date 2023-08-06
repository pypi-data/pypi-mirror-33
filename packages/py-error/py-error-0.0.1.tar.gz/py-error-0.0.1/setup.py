import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="py-error",
    version="0.0.1",
    author="Divyansh Dwivedi",
    author_email="justdvnsh2208@gmail.com",
    description="An easily-extendable error class for use with python classes",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/justdvnsh/py-error",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)