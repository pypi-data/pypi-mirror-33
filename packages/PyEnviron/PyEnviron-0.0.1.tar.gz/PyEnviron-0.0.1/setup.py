import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PyEnviron",
    version="0.0.1",
    author="TheG3ntleman",
    author_email="sriabhirath12@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    description="PyEnvirons is a higher level API of pygame to easily design, devolop and debug environments for your unsupervised AI agent. It is under rapid development and features will be added almost every single day.",
    url="https://github.com/TheG3ntleman/PyEnvirons",
    packages=setuptools.find_packages()
)
