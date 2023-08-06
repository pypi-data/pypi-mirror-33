from __future__ import absolute_import, division, print_function

from setuptools import setup, find_packages


with open('README.md') as f:
    long_description = f.read()


setup(
    name='klab-autotime',
    version='0.0.5.14',
    # cmdclass=versioneer.get_cmdclass(),
    author='Yiran Tao',
    author_email='yt2487@columbia.edu',
    url='https://github.com/gerard0315/klab-autotime',
    description='Modified from Phillip Cloud project Time everything in IPython',
    long_description=long_description,
    license='Apache',
    install_requires=['ipython'],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering',
        'Topic :: Utilities',
    ],
    packages=find_packages(),
)
