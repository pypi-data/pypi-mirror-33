from setuptools import setup, find_packages
from codecs import open
from os import path
from DaPy.version import __version__

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'DaPy/doc/README.md'), encoding='utf-8') as f:
    long_description = f.read()
setup(
    name='DaPy',
    version=__version__,
    description='A light data processing and analysis library for Python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/JacksonWuxs/DaPy',
    author='Xuansheng Wu',
    author_email='wuxsmail@163.com',
    include_package_data = True,  
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    keywords='data science',
    packages=find_packages(),
    project_urls={
        'Bug Reports': 'https://github.com/JacksonWuxs/DaPy',
        'Funding': 'https://donate.pypi.org',
        'Say Thanks!': 'https://github.com/JacksonWuxs/DaPy',
        'Source': 'https://github.com/JacksonWuxs/DaPy',
    },
)
