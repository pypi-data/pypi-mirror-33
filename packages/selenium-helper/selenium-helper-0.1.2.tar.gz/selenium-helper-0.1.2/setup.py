from setuptools import (
	setup,
	find_packages
)

setup(
name = 'selenium-helper',
version = '0.1.2',
author = 'Ammad Khalid',
author_email = 'ammadkhalid12@gmail.com',
packages = find_packages(),
url = 'https://github.com/Ammadkhalid/',
install_requires = ['selenium', 'pandas', 'openpyxl'],
python_requires = '>= 3'
)