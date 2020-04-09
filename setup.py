import pathlib
from setuptools import setup

# The directory containing this file
# HERE = pathlib.Path(__file__).parent

# The text of the README file
# README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="canvas_client",
    version="0.1.0",
    description="Canvas LMS client: Download submissions, upload grades and comments from excel",
    # long_description=README,
    long_description_content_type="text/markdown",
    author="Csanad Sandor",
    author_email="scsanad@cs.ubbcluj.ro",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["canvas_client"],
    include_package_data=True,
    install_requires=[  "jsonpickle", "requests", "pandas", \
                        "pyunpack", "xlwt", "xlrd"],
    entry_points={
        "console_scripts": [
            "canvas_client=canvas_client.__main__:main",
        ]
    },
)
