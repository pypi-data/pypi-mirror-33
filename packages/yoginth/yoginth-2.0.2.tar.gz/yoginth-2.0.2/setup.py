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
    version = "2.0.2",
    description = "The Yoginth CLI",
    author = "Yoginth",
    author_email = "yoginth@zoho.com",
    url = "https://gitlab.com/yoginth/yoginth",
    install_requires=[
        'colorama',
    ],
)
