import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='pyhighlight',
    version='1.0.2',
    author='Tyler Burdsall',
    author_email='tylerburdsall@gmail.com',
    description='Tiny package to help highlight portions of an image with matplotlib',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/iamtheburd/pyhighlight',
    packages=setuptools.find_packages(),
    classified=(
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    )
)