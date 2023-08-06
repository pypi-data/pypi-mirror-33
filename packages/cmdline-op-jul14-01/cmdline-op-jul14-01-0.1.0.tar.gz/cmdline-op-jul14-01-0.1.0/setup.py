import os
import re
from setuptools import setup

version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('optimalprobes/optimalprobes.py').read(),
    re.M
    ).group(1)

with open("README.rst", "rb") as f:
    long_descr = f.read().decode("utf-8")

# Add path to txt files in the macros.py 
dirpath = os.getcwd()
with open("optimalprobes/macros.py", "r+") as f:
	print dirpath
	old = f.read() # read everything in the file
	f.seek(0) # rewind
	f.write("#" + old) # write the new line before
dirpath = os.getcwd()
with open("optimalprobes/macros.py", "r+") as f:
	print dirpath
	old = f.read() # read everything in the file
	f.seek(0) # rewind
	f.write("dirpath=\""+dirpath+"/optimalprobes\"\n" + old) # write the new line before

setup(
    name = "cmdline-op-jul14-01",
    packages = ["optimalprobes"],
    entry_points = {
        "console_scripts": ['optimalprobes = optimalprobes.optimalprobes:main']
        },
    version = version,
    description = "Python command line application for Optimal Probes.",
    long_description = long_descr,
    author = "Shriyaa Mittal",
    author_email = "mittalshriyaa@gmail.com",
    url = "http://www.shuklagroup.org/",
    )
