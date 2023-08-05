from setuptools import setup

setup(
    name = 'writ',
    version = '0.1.1',
    packages = ['writ'],
	entry_points = { 'console_scripts': ['writ=writ.main:main'] },
	author = "jacksonelfers",
    author_email = "JacksonElfers@hotmail.com",
    license = 'Creative Commons Attribution-Noncommercial-Share Alike license',
    long_description = open('README.md').read(),
	long_description_content_type = 'text/markdown'
)