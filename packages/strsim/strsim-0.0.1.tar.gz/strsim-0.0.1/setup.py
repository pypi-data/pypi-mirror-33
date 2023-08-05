import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="strsim",
    version="0.0.1",
    description="A library implementing different string similarity and distance measures",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/luozhouyang/python-string-similarity",
    author="ZhouYang Luo",
    author_email="stupidme.me.lzy@gmail.com",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=["numpy>=1.12.0"],
    license="MIT License",
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    )
)
