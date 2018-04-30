import versioneer
from setuptools import setup, find_packages

setup(
    name='gitstats-dwr',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='gitstats',
    long_description='Statistics for Git Repo',
    url='',

    author='rappdw',
    author_email='rappdw@gmail.com',

    license='MIT',
    keywords='library',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        # Set this topic to what works for you
        'Topic :: Python :: Library',
        # Pick your license as you wish (should match "license" above)
        'License :: MIT',
        'Programming Language :: Python :: 3.5',
    ],

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    include_package_data=True,

    # Alternatively, if you want to distribute just a my_module.py, uncomment
    # this:
    #   py_modules=["my_module"],

    setup_requires=[
        # Setuptools 18.0 properly handles Cython extensions.
        'setuptools>=18.0'
    ],
    install_requires=[
        'dataclasses',
        'multiprocessing_logging'
    ],

    extras_require={
        'dev': [
            'wheel>=0.30.0'
        ],
        'test': [
        ],
    },

    package_data={
        # 'sample': ['package_data.dat'],
    },

    entry_points={
        'console_scripts': [
            'gitstats = gitstats:main',
            'gencsvstats = gitstats.git_csv_generator:gen_csv'
        ],
    },
    # entry_points={
        # 'console_scripts': [
            # 'sample=sample:main',
        # ],
    # },
)
