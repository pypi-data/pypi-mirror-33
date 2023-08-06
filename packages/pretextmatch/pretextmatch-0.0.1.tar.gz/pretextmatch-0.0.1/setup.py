import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pretextmatch",
    version="0.0.1",
    author="William Hanson",
    author_email="dubyuhtee@gmail.com",
    description="Complex text matching, simply",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dubyuhtee/pretext_matcher",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta"
    ),
)