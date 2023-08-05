import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="password_system",
    version="1.0",
    author="jamesg31",
    author_email="jamie.gardner25@gmail.com",
    description="A complete password system.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jamesg31/Password-System",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
