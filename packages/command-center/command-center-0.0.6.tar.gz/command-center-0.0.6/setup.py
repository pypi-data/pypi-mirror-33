from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='command-center',
    version='0.0.6',
    description='Quick method for running frequently used terminal commands.',
    long_description=long_description,
    url='https://github.com/miniscruff/python-command-center',
    author='Ronnie Smith',
    author_email='halfpint1170@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='development',
    package_dir={'': 'src'},
    py_modules=['pcc', 'pccgui', 'utils'],
    install_requires=[
        'click',
    ],
    entry_points={
        'console_scripts': [
            'pcc=pcc:main',
            'pcc-gui=pccgui:main',
        ],
    },
    project_urls={
        'Bug Reports': 'https://github.com/miniscruff/python-command-center/issues', # noqa
        'Source': 'https://github.com/miniscruff/python-command-center',
    },
)
