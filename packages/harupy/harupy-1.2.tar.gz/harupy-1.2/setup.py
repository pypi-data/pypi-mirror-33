from setuptools import setup, find_packages


setup(
	name='harupy',
	version='1.2',
	description='Library for handling Korean Hangul',
	author='Soo Kim',
	author_email='sookim@outlook.jp',
	url='https://github.com/soo-kim/harupy',
	download_url='https://github.com/soo-kim/harupy/archive/1.2.tar.gz',
	packages=find_packages(exclude=['tests']),
	keywords=['korean', 'hangul', 'string'],
	python_requires='>=3',
	include_package_data=True,
	zip_safe=False,
	install_requires=[],
	setup_requires=[],
	dependency_links=[],
	classifiers=[
		'Programming Language :: Python :: 3',
		'Programming Language :: Python :: 3.2',
		'Programming Language :: Python :: 3.3',
		'Programming Language :: Python :: 3.4',
		'Programming Language :: Python :: 3.5',
		'Programming Language :: Python :: 3.6'
	]
)
