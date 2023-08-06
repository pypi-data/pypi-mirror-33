import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="csr_utils",
    version="0.1",
    author="Narges Razavian",
    author_email="nsr3@nyu.edu",
    description="Utility functions for scalable handling of CSR matrices",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/narges-rzv/csr_utils",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    install_requires=['scipy', 'numpy'],
)

