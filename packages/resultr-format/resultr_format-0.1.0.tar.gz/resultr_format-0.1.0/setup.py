import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="resultr_format",
    version="0.1.0",
    author="Hayk Khachatryan",
    author_email="hi@hayk.io",
    description="Making UCL PHAS results better",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/haykkh/resultr",
    packages=setuptools.find_packages(),
    license='MIT',
    install_requires=[
          'inquirer>=2.2.0'
    ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)