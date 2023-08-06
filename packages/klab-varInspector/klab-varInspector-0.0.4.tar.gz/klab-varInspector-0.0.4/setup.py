from __future__ import absolute_import, division, print_function

from setuptools import setup, find_packages


setup(
    name='klab-varInspector',
    version='0.0.4',
    # cmdclass=versioneer.get_cmdclass(),
    author='Yiran Tao',
    author_email='yt2487@columbia.edu',
    description='test',
    # long_description=long_description,
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