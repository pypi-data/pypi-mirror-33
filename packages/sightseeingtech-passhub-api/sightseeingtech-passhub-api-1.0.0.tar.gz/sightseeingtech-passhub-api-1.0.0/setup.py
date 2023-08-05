import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

NAME = "sightseeingtech-passhub-api"
VERSION = "1.0.0"
REQUIRES = ["urllib3 >= 1.15", "six >= 1.10", "certifi", "python-dateutil"]

setuptools.setup(
    name=NAME,
    version=VERSION,
    description='PassHub API Client',
    author='BYM Development LLC',
    author_email='dev@sightseeingtech.com',
    url='https://github.com/BYMdevelopment/passhub-api-client-python',
    keywords=['PassHub', 'SightseeingPass', 'API Client', 'API'],
    install_requires=REQUIRES,
    packages=setuptools.find_packages(),
    long_description=long_description,
    long_description_content_type='text/markdown',
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    )
)


