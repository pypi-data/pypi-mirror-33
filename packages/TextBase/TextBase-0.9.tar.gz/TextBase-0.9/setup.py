from setuptools import setup

with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(name="TextBase",
      version="0.9",
      description="TextBase library to manipulate DBText style data files.",
      long_description=long_description,
      author="Etienne Posthumus",
      author_email="ep@epoz.org",
      url="https://github.com/epoz/textbase/",
      py_modules=["textbase", ],
      classifiers=(
          "Programming Language :: Python :: 2.7",
          "Programming Language :: Python :: 3",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
      ),
      )
