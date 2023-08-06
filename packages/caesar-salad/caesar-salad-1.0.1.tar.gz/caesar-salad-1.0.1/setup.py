from setuptools import setup, find_packages

setup(
    name = 'caesar-salad',
    version = '1.0.1',
    description = 'A command-line tool to crack ROT-n Caesar Ciphers by a brute force attack on a sample of text',
    author = 'amithkk',
    author_email = 'amithkumaran+pypi@gmail.com',
    url = 'https://github.com/amithkk/caesar-salad',
    license = 'GNU GPL v3',
    include_package_data = True,
    packages=find_packages(),
    entry_points = {
       "console_scripts": ['caesar-salad=caesarsalad.caesarsalad:main']
    },
)