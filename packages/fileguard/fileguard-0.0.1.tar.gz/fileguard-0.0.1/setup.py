import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='fileguard',
    packages = ['fileguard'],
    version='0.0.1',
    author='Illya Gerasymchuk',
    author_email='illya@iluxonchik.me',
    description='Preserve the content of your files and directories during testing.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/iluxonchik/fileguard',
    license = 'MIT',
    classifiers=(
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Testing :: Unit',

    ),
    keywords = ['testing',
                'testing tools',
                'test',
                'file',
                'directory',
                'preserve content',
                'backup',
                ],
)
