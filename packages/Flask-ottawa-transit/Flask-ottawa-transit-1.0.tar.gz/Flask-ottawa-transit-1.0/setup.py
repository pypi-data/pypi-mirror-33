"""
Flask-ottawa-transit
-------------

This is the description for that library
"""
from setuptools import setup


setup(
    name='Flask-ottawa-transit',
    version='1.0',
    url='http://github.com/buckley-w-david/Flask-ottawa-transit',
    license='MIT',
    author='David Buckley',
    author_email='buckley.w.david@gmail.com',
    description='Flask extension around the python-ottawa-transit module',
    long_description=__doc__,
    packages=['flask_ottawa_transit'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask>=1.0',
        'python-ottawa-transit>=0.2.0'
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
