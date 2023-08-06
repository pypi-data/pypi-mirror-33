import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PyLOD",
    version="0.1.11",
    author="Panos Mitzias",
    author_email="pmitzias@gmail.com",
    description="PyLOD is a Python wrapper for exposing Linked Open Data from public SPARQL-served endpoints.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/panmitz/PyLOD",
    packages=setuptools.find_packages(),
    install_requires=[
          'sparqlwrapper',
      ],
    classifiers=(
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ),
)

