import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="d4",
    version="0.1.10",
    author="Tatsunori Saito",
    author_email="bbrfkr@gmail.com",
    description="Dock to Develop Dynamic Dockerfile",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pypa/d4",
    packages=setuptools.find_packages(),
    install_requires=[
        "docker",
        "pyyaml"
    ],
    package_data={
        "d4": [
            "data/Dockerfile",
            "data/common.yaml",
            "data/build.yaml",
            "data/tests/*"
        ],
    },
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
    ),
    entry_points={
        "console_scripts":[
            "d4 = d4.d4:main"
        ],
    },
)

