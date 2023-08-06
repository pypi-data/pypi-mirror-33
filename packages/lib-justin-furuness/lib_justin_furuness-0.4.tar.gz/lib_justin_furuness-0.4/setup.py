from setuptools import setup, find_packages

setup(
    name='lib_justin_furuness',
    packages=find_packages(),
    version='0.4',
    description='Test that prints out Justin Furuness',
    author='Justin Furuness',
    author_email='jfuruness@gmail.com',
    url='https://github.com/jfuruness/justin_furuness',
    download_url='https://github.com/jfuruness/justin_furuness',
    keywords=['Furuness', 'furuness', 'pypi', 'package'],  # arbitrary keywords
    install_requires=[
        'pytest==2.9.2'
    ],
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules'],
    entry_points={
        'console_scripts': [
            'justin_furuness = lib_justin_furuness.justin_furuness:print_justin_furuness'
        ]},
)
