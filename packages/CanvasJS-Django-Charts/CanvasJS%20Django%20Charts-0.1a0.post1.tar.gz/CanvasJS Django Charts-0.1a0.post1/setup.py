import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="CanvasJS Django Charts",
    version="0.1a-r1",
    author="Raydel Miranda",
    author_email="raydel.miranda.gomez@gmail.com",
    description="App for charts generation for django apps.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/elasbit/fc-cloudtrails-sdk-py/src/develop/",
    packages=[
        'django_charts',
        'django_charts.migrations',
        'django_charts.templatetags'
    ],
    package_dir={
        'django_charts': 'django_charts'
    },
    package_data={
        'django_charts': ['templates/*']
    },
    classifiers=(
        "Programming Language :: Python :: 2",
        "Operating System :: OS Independent",
    ),
)
