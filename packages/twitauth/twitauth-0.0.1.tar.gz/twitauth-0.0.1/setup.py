import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="twitauth",
    version="0.0.1",
    author="Anish Patel",
    author_email="anishpatel345@gmail.com",
    description="A library to automatically integrate twitter login with database compatibility",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/anish12341/twitauth.git",
    packages=setuptools.find_packages()
)