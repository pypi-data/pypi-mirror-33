import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="smart_append_path",
    version="0.0.1",
    author="duanping",
    author_email="liuan.yla@alibaba-inc.com",
    description="A small import package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lua511/py_smart_append_path.git",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)