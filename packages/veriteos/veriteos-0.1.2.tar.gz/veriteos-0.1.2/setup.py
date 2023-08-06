from setuptools import setup

install_requires = ['requests']

setup(
	name='veriteos',
	packages=['veriteos'],
	version='0.1.2',
	description='Official Python client library for Veriteos API.',
	author='Kyloon Chuah',
	author_email='kyloon@veriteos.com',
	url='https://github.com/veriteos/veriteos-python',
	keywords=['veriteos', 'blockchain'],
	install_requires=install_requires,
	classifiers=[
		'Programming Language :: Python :: 3.5',
		'License :: OSI Approved :: MIT License',
		'Intended Audience :: Developers',
		'Topic :: Software Development :: Libraries'
	]
)
