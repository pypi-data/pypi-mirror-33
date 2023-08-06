from distutils.core import setup
setup(
    name='encase',
    packages=['encase'],
    version='1.1',
    description='A Better Dictionary Class',
    long_description=open('README.rst').read(),
    author='Ryan Miller',
    author_email='ryan@devopsmachine.com',
    license='MIT',
    url='https://github.com/RyanMillerC/encase',
    download_url='https://github.com/RyanMillerC/encase/archive/1.1.tar.gz',
    keywords=['data', 'dictionary'],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities'
    ]
)
