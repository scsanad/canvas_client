import os
from setuptools import setup

# The directory containing this file
HERE = os.path.abspath(os.path.dirname(__file__))

# The text of the README file
with open(os.path.join(HERE, "README.md")) as fid:
    README = fid.read()

# This call to setup() does all the work
setup(
    name="canvas_client",
    version="0.2.1",
    description="Canvas LMS client: Download submissions, upload grades and comments from excel",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/scsanad/canvas_client",
    author="Csanad Sandor",
    author_email="scsanad@cs.ubbcluj.ro",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    packages=["canvas_client"],
    include_package_data=True,
    install_requires=[  "jsonpickle", "requests", "pandas", \
                        "pyunpack", "xlwt", "xlrd"],
    entry_points={
        "console_scripts": [
            "canvas_client=canvas_client.__main__:main"
        ]
    },
)
