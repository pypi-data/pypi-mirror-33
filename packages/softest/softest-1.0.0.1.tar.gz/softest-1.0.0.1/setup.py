import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="softest",
    version="1.0.0.1",
    author="Nick Umble",
    author_email="nicholas.umble@perficient.com",
    description="Supports soft assertions in extending the unittest.TestCase class",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://i.dont.have.it.on.github.com",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
