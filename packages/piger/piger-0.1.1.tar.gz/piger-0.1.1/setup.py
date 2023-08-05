import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="piger",
    version="0.1.1",
    author="pigbrother",
    author_email="2751054328@qq.com",
    description="猪猪的wheel",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/pigbrother_1/pig",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
