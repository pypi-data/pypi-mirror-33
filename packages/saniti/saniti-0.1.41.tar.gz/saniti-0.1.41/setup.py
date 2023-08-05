import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="saniti",
    version="0.1.41",
    author="JBMountford",
    author_email="jbm112358@gmail.com",
    description="Sanitise text while keeping your sanity",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ChamRoshi/Saniti",
    install_requires=['gensim','nltk'],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]

)
