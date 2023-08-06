import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("version", "r") as fh:
    version = fh.read().strip()

with open("requirements.txt", "r") as fh:
    requirements = fh.readlines()
    requirements = [r.strip() for r in requirements if r.strip() != ""]

setuptools.setup(
    name="xalanih",
    version=version,
    author="Hereman Nicolas",
    author_email="nicolas.hereman@gmail.com",
    description="Xalanih is a python script made to help you version your SQL database.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nhereman/Xalanih",
    packages=setuptools.find_packages(),
    install_requires=requirements,
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
