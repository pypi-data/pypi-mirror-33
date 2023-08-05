import setuptools

with open( "README.md", "r" ) as fh:
    long_description = fh.read()

setuptools.setup(
    name = "flask-gae-users",
    version = "0.0.1",
    license = "MIT",
    author = "Daniel 'Vector' Kerr",
    author_email = "vector@vector.id.au",
    description = "Provide route decorators for Google App Engine users",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    keywords = "flask google app engine gae user users decorator",
    url = "https://gitlab.com/vector.kerr/flask-gae-users",
    packages = setuptools.find_packages(),
    install_requires = [ 'flask' ],
    classifiers = (
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
