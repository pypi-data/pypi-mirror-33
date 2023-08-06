"""
Django-Gtranslate
-------------
A Django app to add Googletrans google translation to the template 
with ability to cache translation to external pretty .json file.
"""
from setuptools import setup, find_packages


setup(
    name='Django-Gtranslate',
    version='0.1.2',
    packages=find_packages(),
    url='https://github.com/mrf345/django_gtranslate/',
    download_url='https://github.com/mrf345/django_gtranslate/archive/0.1.2.tar.gz',
    license='MIT',
    author='Mohamed Feddad',
    author_email='mrf345@gmail.com',
    description='Googletrans google translation django app',
    long_description=__doc__,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'django',
        'googletrans'
    ],
    keywords=['django', 'extension', 'google', 'translate', 'googletrans', 'json'],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)