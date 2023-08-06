from setuptools import setup, find_packages

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='ocdsextensionregistry',
    version='0.0.4',
    author='James McKinney',
    author_email='james@slashpoundbang.com',
    url='https://github.com/open-contracting/extension_registry.py',
    description="Eases access to information from the extension registry of the Open Contracting Data Standard",
    license='BSD',
    packages=find_packages(),
    long_description=long_description,
    install_requires=[
        'requests',
    ],
    extras_require={
        'test': [
            'coveralls',
            'pytest',
            'pytest-cov',
        ],
    },
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3.6',
    ],
)
