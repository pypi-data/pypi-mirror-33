import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ani.py",
    version="0.2.1",
    author="Joel Widmer",
    author_email="joel.widmer.wj@gmail.com",
    description="Python interface for anime APIs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    install_requires=[
        "requests",
        "requests-toolbelt",
    ],
)
