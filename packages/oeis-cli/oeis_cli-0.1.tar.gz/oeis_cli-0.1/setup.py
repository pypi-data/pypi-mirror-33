from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='oeis_cli',
      packages=['oeis_cli'],
      version='0.1',
      description='Command-line interface for OEIS.',
      author='Dominic Benjamin',
      author_email='domfbenjamin@gmail.com',
      long_description=long_description,
      url='https://github.com/dfbenjamin/oeis-cli/',
      entry_points = {
          'console_scripts': ['oeis=oeis_cli.oeis:main'],
      },
      classifiers=(
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Programming Language :: Python",
      ),
)
