from setuptools import setup

setup (
	name = 'aiorule34',
	version = '1.2.0',
	description = 'an async wrapper for rule34.xxx',
	url = 'https://github.com/Apache-HB/aiorule34',
	author = 'Elliot Haisley',
	author_email = 'apachehb@gmail.com',
	license = 'Apache2.0',
	packages = ['aiorule34'],
	install_requires = [
		'aiohttp',
		'defusedxml'
	],
	keywords = [
		'rule34',
		'async',
		'api',
		'wrapper',
		'porn'
	],
	zip_safe = False
)