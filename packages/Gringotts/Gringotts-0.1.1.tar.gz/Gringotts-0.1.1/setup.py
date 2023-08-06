import setuptools

with open('README.md', 'r') as fh:
	long_description = fh.read()

setuptools.setup(
	name='Gringotts',
	version='0.1.01',
	author='J. Chamness',
	author_email='jchamness@gmail.com',
	description='Tools for personal financial planning',
	long_description=long_description,
	long_description_content_type='text/markdown',
	url='https://pypi.org/project/gringotts/',
	packages=setuptools.find_packages(),
	classifiers=(
		'Programming Language :: Python :: 3',
		'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
		'Operating System :: OS Independent',
	),
)
