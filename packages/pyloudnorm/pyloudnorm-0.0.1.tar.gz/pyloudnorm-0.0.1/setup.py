from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='pyloudnorm',
      version='0.0.1',
      description='Implementation of ITU-R BS.1770-4 loudness algorithm in python',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/csteinmetz1/pyloudnorm',
      author='Christian Steinmetz',
      author_email='cjstein@clemson.edu',
      packages=['pyloudnorm'],
      install_requires=['scipy>=1.0.1',
                        'numpy>=1.14.2',
                        'matplotlib>=2.1.1'],
      classifiers=(
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
      ),
)