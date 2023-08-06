import setuptools

with open( 'README.md', 'r' ) as fh:
    long_description = fh.read()

setuptools.setup(
    name =              'pyri',
    version =           '0.0.1',
    author =            'pyq',
    author_email =      'vcsqlt@gmail.com',
    description =       'The pyri package reads a ...',
    long_description =  long_description,
    long_description_content_type = 'text/markdown',
    url =               'https://github.com/pypa/example-project',
    packages =          setuptools.find_packages(),
    classifiers =       (
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
                        ),
)
