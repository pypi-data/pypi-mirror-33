import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="fynd",
    version="1.3.0",
    author="Ahmed Noor",
    author_email="m.ahmednoor7@yahoo.com",
    description="A super simple string searching library for complex list/dict structures",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ahmednooor/fynd",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)