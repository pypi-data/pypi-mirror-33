import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hello_pi",
    version="0.0.1",
    author="Samlet Wu",
    author_email="xiaofei.wu@gmail.com",
    description="A small pypi package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/samlet/hello-pi",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
