import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pycommon_andreacioni",
    version="0.0.1",
    author="Andrea Cioni",
    description="Common utility classes from some Python projects",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/andreacioni/pycommon",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)