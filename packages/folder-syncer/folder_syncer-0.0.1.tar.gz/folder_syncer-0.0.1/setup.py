from setuptools.command.install import install
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="folder_syncer",
    version="0.0.1",
    author="Billy Su",
    author_email="billysu.4195@gmail.com",
    description="A simple folder syncer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/billy4195/folder_syncer",
    packages=setuptools.find_packages(),
    install_requires=[
        "kivy>=1.10.0",
        "Cython>=0.25.2",
    ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ),
    data_files=[
        ("license", ["LICENSE"])
    ],
    license="Apache-2.0",
)
