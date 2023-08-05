import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hellp",
    version="0.0.1",
    author="Mohammad Hossein Sekhavat",
    author_email="sekhavat17@gmail.com",
    description="Python Pipe Operator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/python-pipe/hellp.git",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
from os import path
from io import open

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='hellp',  # Required
    version='0.0.0',  # Required
    description='Pipe Helper',  # Required
    long_description=long_description,  # Optional
    long_description_content_type='text/markdown',  # Optional (see note above)
    url='https://github.com/python-pipe/hellp.git',  # Optional
    author='Mohammad Hossein Sekhavat',  # Optional
    author_email='sekhavat17@gmail.com',  # Optional
    classifiers=[  # Optional
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    keywords='pipe helper tool magrittr data science',  # Optional
    packages=find_packages(exclude=[]),  # Required
    install_requires=['toolz==0.9.0'],  # Optional
    extras_require={  # Optional
        'dev': ['check-manifest'],
        'test': ['coverage'],
    },
    package_data={  # Optional
    },
    entry_points={  # Optional
    },
    # project_urls={  # Optional
    #     'Bug Reports': 'https://github.com/pypa/sampleproject/issues',
    #     'Funding': 'https://donate.pypi.org',
    #     'Say Thanks!': 'http://saythanks.io/to/example',
    #     'Source': 'https://github.com/pypa/sampleproject/',
    # },
)
