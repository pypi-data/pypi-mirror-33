import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="inmation-api-client",
    version="0.1.8",
    author="Alexandr Sapunji",
    author_email="alexandr.sapunji@inmation.com",
    license='MIT',
    description="API client for system:inmation.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://inmation.com",
    packages=setuptools.find_packages(),
    install_requires=[
          'websockets>=5.0',
    ],
    classifiers=(
		"Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.5",
        "Operating System :: OS Independent",
    ),
)