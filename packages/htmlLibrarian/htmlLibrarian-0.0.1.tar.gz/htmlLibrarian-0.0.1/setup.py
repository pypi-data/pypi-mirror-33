from setuptools import setup, find_packages


with open('readme.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='htmlLibrarian',
    version='0.0.1',
    description='Never ever scrape the html off of a site multiple times ever again.',
    long_description=readme,
    author='Alex Sieusahai',
    author_email='alexsieu14@gmail.com',
    url='https://github.com/alexsieusahai/Librarian',
    license=license,
    packages=find_packages(exclude=('tests'))
)
