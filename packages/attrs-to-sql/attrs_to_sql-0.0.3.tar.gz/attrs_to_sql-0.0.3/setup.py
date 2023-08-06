import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="attrs_to_sql",
    version="0.0.3",
    author="potykion",
    author_email="potykion@gmail.com",
    description="Convert attrs class to CREATE TABLE command.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/potykion/attrs_to_sql",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)