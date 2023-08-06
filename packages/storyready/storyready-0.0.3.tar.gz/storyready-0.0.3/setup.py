import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="storyready",
    version="0.0.3",
    author="David Clarke",
    author_email="dnjclarke@gmail.com",
    description="A simple set of checks for typical Agile Story Readiness criteria (GWTS, Story Format,...)",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/DNJC/storyready",
    packages=setuptools.find_packages()
)