import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyow",
    version="0.0.4",
    author="Henrik Andersson",
    author_email="henrik@http418.se",
    description="A function argument validation for humans",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/limelights/pyow",
    packages=setuptools.find_packages(),
    install_requires=[
        'python-dateutil',
    ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
