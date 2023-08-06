import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="backalla_utils",
    version="0.0.5",
    author="Tushar Pawar",
    author_email="gmail@tusharpawar.com",
    description="Collection of frequently used utility functions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Backalla/Backalla-utils",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ),
)