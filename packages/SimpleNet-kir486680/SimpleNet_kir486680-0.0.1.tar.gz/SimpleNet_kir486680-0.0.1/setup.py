import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="SimpleNet_kir486680",
    version="0.0.1",
    author="Kyrylo",
    author_email="kir486680@gmail.com",
    description="Package that helps to create neural nets",
    long_description="Net",
    long_description_content_type="text/markdown",
    url="https://github.com/kir486680",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)