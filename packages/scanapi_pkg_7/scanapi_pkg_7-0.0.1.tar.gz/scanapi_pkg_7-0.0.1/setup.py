import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="scanapi_pkg_7",
    version="0.0.1",
    author="Example Author",
    author_email="author@example.com",
    description="A small example package",
   #include_package_data="scanapi_pkg/_scanapi.cpython-35m-x86_64-linux-gnu.so",
    package_data = {
        '': ['*.so']
        },
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/example-project",
    packages=setuptools.find_packages(),
   # classifiers=(
   #     "Programming Language :: Python :: 3",
   #     "License :: OSI Approved :: MIT License",
   #     "Operating System :: OS Independent",
    #),
)
