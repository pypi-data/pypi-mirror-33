from setuptools import setup

with open('README.md') as file:
    long_description = file.read()

setup(
    name='pysshops',
    version=' 0.1.0',
    author='Lorenzo Gaggini',
    author_email='lg@lgaggini.net',
    packages=['pysshops'],
    url='https://github.com/lgaggini/pysshops',
    license='LICENSE',
    keywords=['SSH', 'OPS', 'AUTOMATION'],
    description='Human readable slim REST client',
    long_description=long_description,
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 4 - Beta',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Topic :: System :: Installation/Setup'
    ],
    install_requires=[
        'paramiko'
    ],
)
