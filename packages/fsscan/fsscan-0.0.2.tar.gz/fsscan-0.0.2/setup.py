import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fsscan",
    version="0.0.2",
    author="krakozaure",
    author_email="",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/krakozaure/fsscan",
    packages=setuptools.find_packages(),
    install_requires=[
        'scandir;python_version<"3.5"'
    ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
