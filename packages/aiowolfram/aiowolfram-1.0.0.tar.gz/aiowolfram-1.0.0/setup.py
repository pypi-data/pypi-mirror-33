from setuptools import setup

setup (
	name = 'aiowolfram',
	version = '1.0.0',
	description = 'an async wrapper for wolfram-alphas web api',
	url = 'https://github.com/Apache-HB/aiowolfram',
	author = 'Elliot Haisley',
	author_email = 'apachehb@gmail.com',
	license = 'Apache2.0',
	packages = ['aiowolfram'],
	install_requires = [
		'aiohttp'
	],
	keywords = [
		'wolfram',
		'wolframalpha',
		'wolfram-alpha',
		'async',
		'json'
	],
	zip_safe = False
)