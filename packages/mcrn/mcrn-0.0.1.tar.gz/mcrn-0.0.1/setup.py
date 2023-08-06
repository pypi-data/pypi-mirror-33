import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mcrn",
    version="0.0.1",
    author="Johan Bloemberg",
    author_email="mcrn@ijohan.nl",
    description="Configuration management framework for small networks.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aequitas/mcrn",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
