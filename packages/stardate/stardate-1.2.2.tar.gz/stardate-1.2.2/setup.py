from setuptools import setup

setup(name='stardate',
    version='1.2.2',
    description='Represent points in time as fractional years in UTC',
    license='MIT',
    packages=['stardate'],
    author='Chris Oei',
    author_email='chris.oei@gmail.com',
    install_requires=[
        'python-dateutil',
    ],
    scripts=['bin/stardate'],
    zip_safe=False)

