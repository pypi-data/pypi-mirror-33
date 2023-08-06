import os
import sys
import setuptools
from subprocess import call
from ctypes.util import find_library
from setuptools.dist import Distribution
from setuptools.command.build_py import build_py


class BinaryDistribution(Distribution):

    def is_pure(self):
        return False

    def root_is_pure(self):
        return False


class BuildSharedLib(build_py):

    def run(self):
        if not self.dry_run:

            # find libundumpi and build it, if not installed
            lib = find_library("undumpi")
            if not lib or "libundumpi.so" not in lib:
                cwd = os.getcwd()
                repo_url = "https://github.com/sstsimulator/sst-dumpi"
                commit_hash = "5744b8d8f8372171c81f55be43ed658bde6a58fa"
                call(["git", "clone", repo_url])

                os.chdir("sst-dumpi")
                call(["git", "checkout", commit_hash])
                call(["./bootstrap.sh"])
                call(["./configure", "--disable-static", "--prefix={0}/pydumpi".format(cwd)])
                call(["make"])
                call(["make", "install"])
                os.chdir(cwd)

        build_py.run(self)


with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="pydumpi",
    version="0.1.0",
    author="Tobias Schwackenhofer",
    author_email="tobiasschw@gmail.com",
    description="Python bindings for the sst-dumpi trace format.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/justacid/pydumpi",
    distclass=BinaryDistribution,
    packages=["pydumpi"],
    package_data={"pydumpi": ["lib/libundumpi.so.8.0.0"]},
    python_requires=">=3.4",
    cmdclass={"build_py": BuildSharedLib},
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    )
)
