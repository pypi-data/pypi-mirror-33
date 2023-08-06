import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="django-distance-field",
    version="0.2",
    author="Ian Shurmer",
    author_email="ian@squarehost.co.uk",
    description="Django model field to allow storage of a distance (with units).",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/squarehost/django-distance-field",
    packages=setuptools.find_packages(),
    install_requires=[
        "django>=1.7"
    ],
    classifiers=(
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        'Framework :: Django',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)