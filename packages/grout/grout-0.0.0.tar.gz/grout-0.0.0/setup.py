import setuptools

def readme():
    with open('README.md') as f:
        return f.read()

setuptools.setup(
    name="grout",
    version="0.0.0",
    author="Azavea, Inc.",
    author_email='info@azavea.com',
    description="Placeholder for the Grout package.",
    long_description=readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/azavea/grout",
    packages=setuptools.find_packages(exclude=['tests']),
)
