from setuptools import setup, find_packages
 
setup(
    name='UsefulDB',
    version='1.0.4',
    description='Simplest framework for SQL databases control',
    packages=find_packages(),
    author='Elisey Sharov',
    author_email='elisei.sharow@yandex.ru',
    url='http://github.com/ZerZru/UsefulDB/',
    install_requires=[
        'requests>=2.18.4',
        'pymysql>=0.7.2',
        'BeautifulSoup4>=4.6.0',
    ],
)