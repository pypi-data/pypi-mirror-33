import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="os-acc",
    version="0.0.0",
    author="Xinran Wang",
    author_email="xin-ran.wang@intel.com",
    description="A library which implements Nova/Cyborg interaction",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/os-acc",
    packages=setuptools.find_packages(),
)
