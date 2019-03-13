from setuptools import setup
from pathlib import Path

here = Path(__file__).parent

with (here/'README.md').open(encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='spsearch',
    version='0.1.0',
    description='Python tools to get species data from various API.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/AzukiOtter/spsearch',
    author='AzukiOtter',
    author_email='ogran.std@gmail.com',
    license='GPL-3.0',
    keywords='bioinformatics biology biodiversity species',
    python_requires='>=3.6, <4',
    packages=['spsearch'],
    install_requires=['aiohttp>=3.3.0'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
