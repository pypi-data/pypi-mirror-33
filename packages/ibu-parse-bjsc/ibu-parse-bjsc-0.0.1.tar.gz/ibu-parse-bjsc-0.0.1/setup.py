from setuptools import setup, find_packages

setup(
    name = "ibu-parse-bjsc",
    version = "0.0.1",
    keywords = ("pip", "ibu", "bjsc"),
    description = "parse .bjsc files to objective-c files",
    long_description = "parse .bjsc files to objective-c files",
    license = "MIT Licence",
    author = "shanks",
    author_email = "gyjjone@163.com",

    packages = find_packages(),
    include_package_data = True,
    platforms = "any",
    install_requires = []
)