"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name='tec.ic.ia.p2.g05',  # Required

    version='4.0.0',  # Required

    py_modules=['tec.ic.ia.p2.g05'],

    description='g',  # Required

    long_description=long_description,  # Optional

    url='',  # Optional

    author='JoseMora/DylanRodriguez/KarinaZeledon',  # Optional

    author_email='',  # Optional

    classifiers=[  # Optional
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        
    ],

    keywords='',  # Optional

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),  # Required

    install_requires=['pandas==0.19.1', 'pyDatalog==0.17.1'],  # Optional

    extras_require={  # Optional
        
    },

    package_data={  # Optional
        
    },

    data_files=[],  # Optional

    entry_points={  # Optional
        
    },

    project_urls={  # Optional
        
    },
)
