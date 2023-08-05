import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pymysqlbatchimport",
    version="0.4.1a",
    author="Duc-Anh Le",
    author_email="ducanh.le@cdelta.xyz",
    description="A python wrapper of MySql import tools",
    long_description=long_description,
    url="https://github.com/GoPlan/pymysqlbatchimport.git",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
    )
)
