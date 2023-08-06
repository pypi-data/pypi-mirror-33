from setuptools import setup, find_packages


setup(
    name='kameris-formats',
    version='1.0.1',
    description=('Reader and writer implementations for the file formats used '
                 'by kameris-backend.'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering'
    ],
    author='Stephen',
    author_email='stephsolis@gmail.com',
    url='https://github.com/stephensolis/kameris-formats/',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'scipy'
    ]
)
