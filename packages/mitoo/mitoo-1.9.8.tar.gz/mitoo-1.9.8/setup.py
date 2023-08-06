import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="mitoo",
    version="1.9.8",
    author="Sobhan Kumar Lenka",
    author_email="sobhanlenka@gmail.com",
    description="Python based chatbot framework with voice output",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sobhanlenka/mitoo",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)