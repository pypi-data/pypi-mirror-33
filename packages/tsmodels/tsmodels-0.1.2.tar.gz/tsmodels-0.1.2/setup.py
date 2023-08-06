import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="tsmodels",
    version="0.1.2",
    author="Jack Dry",
    author_email="jack_dry@outlook.com",
    description="A package to build time series models.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    #url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    package_data={'tsmodels': ["data/facebook_returns.csv", 
                               "data/apple_returns.csv"]},
    include_package_data=True,
    classifiers=(
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ),
)
    