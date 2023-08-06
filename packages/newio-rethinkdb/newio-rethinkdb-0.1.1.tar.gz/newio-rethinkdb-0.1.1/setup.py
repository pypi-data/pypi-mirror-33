from setuptools import setup, find_packages

setup(
    name='newio-rethinkdb',
    version='0.1.1',
    keywords='newio rethinkdb async driver',
    description='Newio + RethinkDB: Async RethinkDB driver',
    long_description=__doc__,
    author='guyskk',
    author_email='guyskk@qq.com',
    url='https://github.com/guyskk/newio-rethinkdb',
    license='MIT',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        'rethinkdb>=2.3.0',
        'newio>=0.4.1',
    ],
    extras_require={
        'dev': [
            'invoke==1.0.0',
            'pre-commit==1.4.1',
            'wheel==0.30.0',
            'twine==1.9.1',
            'pytest==3.6.2',
            'pytest==cov-2.5.1',
            'newio-kernel==0.4.1',
            'bumpversion==0.5.3',
        ]
    },
    zip_safe=False,
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
