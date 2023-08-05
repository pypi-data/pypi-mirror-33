import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name="mctool",
    version="0.0.1a1",
    author="hebinhao",
    author_email="hebinhao1993@outlook.com",
    description="machine learning core tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/hebinhao1993/mctool",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ),
)
