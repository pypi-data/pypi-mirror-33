from setuptools import setup, find_packages

setup(
    name='htmlLibrarian',
    version='0.0.2',
    description='Never ever scrape the html off of a site multiple times ever again.',
    long_description='Never ever ever scrape the html off of a site multiple times ever again.',
    author='Alex Sieusahai',
    author_email='alexsieu14@gmail.com',
    url='https://github.com/alexsieusahai/Librarian',
    license='MIT License',
    packages=find_packages(exclude=('tests'))
)
