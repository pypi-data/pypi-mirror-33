import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    install_requires = [line.strip('\n') for line in fh.readlines() if not line.strip().startswith('#') and line.strip()]

setuptools.setup(
    name="pykit-bsc",
    version="0.0.1",
    author="Zhang Yanpo",
    author_email="drdr.xp@gmail.com",
    description="a collection of toolkit lib for distributed system development in python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bsc-s2/pykit",
    packages=setuptools.find_packages(),
    exclude_package_date={'':['.gitignore', '.git']},
    install_requires=install_requires,
    classifiers=(
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
