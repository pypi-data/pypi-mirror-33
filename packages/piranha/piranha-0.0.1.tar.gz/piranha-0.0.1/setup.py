import setuptools
from version import __version__

with open("README.md", "r") as fh:
    long_description = fh.read()

version = '.'.join(str(x) for x in __version__)

setuptools.setup(
    name="piranha",
    version=version,
    author="Jens Schaa",
    author_email="jens.schaa@posteo.de",
    description="My most common boto3 use cases",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/redvox/piranha",
    packages=setuptools.find_packages(),
    classifiers=(
        "Development Status :: 1 - Planning",
        "Programming Language :: Python :: 3",
        'Intended Audience :: Developers',
        "Operating System :: OS Independent",
    )
)
