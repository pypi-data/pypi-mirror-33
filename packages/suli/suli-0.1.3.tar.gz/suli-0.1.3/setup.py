import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="suli",
    version="0.1.3",
    author="Marcelo Jara",
    author_email="marcelo@trazolabs.com",
    description="A template renderer",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/trazolabs/suli",
    packages=setuptools.find_packages(),
    install_requires=[
        'reportlab',
        'wand',
        'jinja2',
    ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ),
)
