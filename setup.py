import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django-dookan", # Replace with your own username
    version="0.0.1",
    author="Md Nazmul Hasan",
    author_email="hasan08sust@gmail.com",
    description="A Django package to maintain cart system of a online shopping site.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/farhapartex/django-dookan",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)