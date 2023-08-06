import setuptools

# with open("README.md", "r") as fh:
#     long_description = fh.read()

setuptools.setup(
    name="zuorapy",
    version="0.0.2",
    author="ihong5",
    author_email="ihong3589@gmail.com",
    description="Zuora Rest Client for Python",
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/ihong5/zuorapy",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)