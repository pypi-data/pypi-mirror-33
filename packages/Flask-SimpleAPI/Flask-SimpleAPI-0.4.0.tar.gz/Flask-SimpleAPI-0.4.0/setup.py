"""
Flask-SimpleAPI
-------------

Very simple way to create an API with Flask and MongoDB:
- simple route
- auto detect and render json if dict, list or MongoEngine object
"""
from setuptools import setup, find_packages
packages = find_packages()

setup(
    name='Flask-SimpleAPI',
    version='0.4.0',
    url='http://bkinno.pro',
    license='MIT',
    author='Bkinno',
    author_email='tronghieu.ha@gmail.com',
    description='Very simple way to create an API with Flask',
    packages=packages,
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'flask',
        'mongoengine'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
