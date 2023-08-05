import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    requirements = fh.read().splitlines()

setuptools.setup(
    name="mangoml",
    version="0.0.2",
    author="Gustavo Santos",
    author_email="gustavohas@outlook.com",
    description="Simple Machine Learning library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/gustavosantos/bam_kaggle",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    install_requires=requirements,
)
