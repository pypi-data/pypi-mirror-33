import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="audentes",
    version="0.1.6",
    author="Magnus Odman",
    author_email="magnus.odman@gmail.com",
    description="A package for writing component tests with docker compose",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/magnus.odman/audentes",
    packages=setuptools.find_packages(),
    install_requires=[
          'requests', 'ruamel.yaml'
      ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
