from setuptools import setup

with open("README.md", 'r') as f:
    long_description = f.read()

setup(
    name='gen_pdf_prices',
    version='0.0.1',
    description='Generate pdf file with prices',
    long_description=long_description,
    author='Druta Ruslan',
    author_email='r.druta@dekart.com',
    packages=['gen_pdf_prices'],
    install_requires=['reportlab'],
)
