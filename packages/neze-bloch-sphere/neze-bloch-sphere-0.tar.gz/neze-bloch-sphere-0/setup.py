import setuptools
with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='neze-bloch-sphere',
    version='0',
    author="Clement Durand",
    author_email="durand.clement.13@gmail.com",
    description="Bloch sphere simulation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
    ),
    install_requires=['matplotlib','numpy'],
)
