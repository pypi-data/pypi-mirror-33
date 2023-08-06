import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="safepass",
    version="0.0.1",
    author="Corey McCandless",
    author_email="crm1994@gmail.com",
    description=(
        "Check passwords against "
        "https://haveibeenpwned.com/API/v2#PwnedPasswords"
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cmccandless/safepass",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
