import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="zixi_api",
    version="0.0.1",
    author="James Fining",
    author_email="jfining@gmail.com",
    description="Python-based Zixi API wrapper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jfining/zixi-api",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ),
    install_requires=[
        "requests >= 2.18.4"
    ]
)

