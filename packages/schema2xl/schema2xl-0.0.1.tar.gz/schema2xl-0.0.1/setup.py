from setuptools import setup
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

requires = ['openpyxl', 'pymysql']

setup(
    name='schema2xl',
    version='0.0.1',
    description='DB schema to xlsx',
    long_description=long_description,
    # long_description_content_type='text/markdown',
    url='https://github.com/sohgett/schema2xl',
    author='Toru Tanaka',
    author_email='sohgett@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='mysql excel',
    packages=[
        'schema2xl',
    ],
    install_requires=requires,
    license='MIT',
)
