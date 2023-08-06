import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="Jarvis_mini",
    version="0.0.2",
    author="Mayur Chhapra",
    author_email="mayurchhapra@gmail.com",
    description="Automated Hardware Scripe.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mayurchhapra/education_theses",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)