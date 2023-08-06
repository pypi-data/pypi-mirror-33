import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pubg-api",
    version="0.0.2",
    author="Michel Wilhelm",
    author_email="michelwilhelm@gmail.com",
    description="PUBG API client",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/imakecodes/pubg",
    packages=setuptools.find_packages(),
    install_requires=[
      'requests>=2.19.1',
  ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)