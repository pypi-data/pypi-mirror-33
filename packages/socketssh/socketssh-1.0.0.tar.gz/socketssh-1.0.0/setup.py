import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="socketssh",
    version="1.0.0",
    author="Jiegl",
    author_email="jiegl1@lenovo.com",
    description="The C/S architecture controls the SSH client for a long time",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/578010377/PythonScript/tree/master/socketssh",
    packages=setuptools.find_packages(),
    install_requires=['pika'],
    classifiers=(
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
