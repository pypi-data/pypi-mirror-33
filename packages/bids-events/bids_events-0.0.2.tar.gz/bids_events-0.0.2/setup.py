import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="bids_events",
    version="0.0.2",
    author="Bruno Melo",
    author_email="bruno.melo@idor.org",
    description="A package to export events using log files from presentation software.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/InstitutoDOr/bids_events",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)