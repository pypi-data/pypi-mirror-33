import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "yoginth",
    packages = ["yoginth"],
    entry_points = {
        "console_scripts": ['yoginth = yoginth.yoginth:main']
        },
    long_description = long_description,
    long_description_content_type = "text/markdown",
    version = "2.0.7",
    description = "The Yoginth CLI",
    author = "Yoginth",
    author_email = "yoginth@zoho.com",
    url = "https://yoginth.ml",
    classifiers=(
        "Programming Language :: Python",
        "Natural Language :: English",
        "Environment :: Console",
        "Operating System :: OS Independent",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
    ),
    project_urls={
        'Patreon': 'https://www.patreon.com/yoginth',
        'Source': 'https://gitlab.com/yoginth/yoginth',
    },
    install_requires=[
        'colorama',
    ],
)
