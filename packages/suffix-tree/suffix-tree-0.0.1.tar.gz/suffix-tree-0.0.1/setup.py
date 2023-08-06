import setuptools

with open ("README.rst", "r") as fh:
    long_description = fh.read ()

setuptools.setup (
    name="suffix-tree",
    version="0.0.1",
    author="Marcello Perathoner",
    author_email="marcello@perathoner.de",
    description="A naive suffix tree",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/cceh/suffix-tree",
    packages=setuptools.find_packages (),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ),
)
