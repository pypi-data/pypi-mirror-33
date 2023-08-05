from setuptools import setup
from setuptools import find_packages

setup(
    name='metaquant',
    version='0.1.0',
    packages=find_packages(exclude=['tests*']),
    url='https://github.com/caleb-easterly/metaquant',
    license='GPL',
    author='caleb',
    author_email='easte080@umn.edu',
    description='Quantitative microbiome analysis',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: MacOS',
        'Operating System :: Unix',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Intended Audience :: Science/Research'
    ],
    install_requires=[
        'pandas',
        'ete3',
        'goatools',
        'wget',
        'numpy',
        'statsmodels'
    ],
    python_requires='>=3.5',
)
