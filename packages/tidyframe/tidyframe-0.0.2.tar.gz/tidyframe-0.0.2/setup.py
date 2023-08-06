from setuptools import setup, find_packages

LONG_DESCRIPTION = """
Overview
--------------

+ Clean pandas DataFrame to tidy DataFrame
+ Inspired by tidyr in R
+ Goal: Help you to create **tidy Pandas Dataframe**
+ Wapper window function from DataFrame
+ Implement R function *tidyr::gather* and *tidyr:spread* using python

"""

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Operating System :: OS Independent',
    'Intended Audience :: Science/Research', 'Programming Language :: Python',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6', 'Programming Language :: Cython',
    'Topic :: Scientific/Engineering'
]

setup(
    name='tidyframe',
    version=open('VERSION').read().strip(),
    author='Hsueh-Hung Cheng',
    author_email='jhengsh.email@gmail.com',
    url='https://github.com/Jhengsh/tidyframe',
    description='Clean pandas DataFrame to Tidy DataFrame',
    long_description=LONG_DESCRIPTION,
    classifiers=CLASSIFIERS,
    keywords=['pandas', 'tidy'],
    packages=find_packages(),
    license='MIT',
    platforms='any',
    python_requires='!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*,!=3.4.*',
    install_requires=["pandas", "funcy"],
)
