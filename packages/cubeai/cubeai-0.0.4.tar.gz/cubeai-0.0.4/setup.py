import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cubeai",
    version="0.0.4",
    author="Ran Shaham",
    author_email="ran.shaham1@mail.huji.ac.il",
    description="an AI solver for the Rubik's Cube",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.cs.huji.ac.il/ransha/ai_project",
    packages=setuptools.find_packages(),
    install_requires=[
        'numpy',
    ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # choose a license
        "Operating System :: OS Independent",
    ),
)
