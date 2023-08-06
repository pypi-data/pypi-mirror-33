import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="IDEA Wrapper",
    version="0.0.1",
    author="Alexander Baron",
    description="A readonly wrapper for the IDEA Python integration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    install_requires=[
        #"re",
        #"win32com.client",
        "datetime",
    ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
