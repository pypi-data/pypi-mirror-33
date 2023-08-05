from setuptools import setup

def readme():
	with open('README.rst') as f:
		return f.read()

setup(name='booksread',
	  version='0.0.1',
	  description='get all the stats related words from book',
	  keywords='book word autocomplete suggest data \
	  			Google author chain machine learning \
	  			Umesh Joshi',
	  author='Umesh Joshi',
	  author_email='umesh14el007@gmail.com',
	  licence='MIT',
	  packages=['booksread'], #for server
	  install_requires=['bottle', 'PyPDF2', 'textract', 'nltk'],
	  url='https://github.com/Umesh8Joshi/BooksWord',
	  scripts=['bin/booksread_server.py'],
	  test_suite='nose.collector',
	  test_require=['nose'],
	  include_package_data=True,
	  zip_safe=False)