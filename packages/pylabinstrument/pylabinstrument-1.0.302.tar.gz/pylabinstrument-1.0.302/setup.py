import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pylabinstrument",
    version="1.0.302",
    author="Pisek Kultavewuti",
    author_email="psk.light@gmail.com",
    description="tools to control equipment such as motors, power meters, camera, etc",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/psklight/pylabinstrument",
    packages=setuptools.find_packages(),
    install_requires = ['numpy', 'pandas'],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: Microsoft :: Windows",
    ),
)