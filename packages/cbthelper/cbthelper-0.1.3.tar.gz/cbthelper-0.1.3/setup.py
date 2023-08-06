import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='cbthelper',
    version='0.1.3',
    author='Tim Hamilton',
    author_email='timh@crossbrowsertesting.com',
    description='a helper library for cross browser testing\'s selenium api',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/crossbrowsertesting/cbthelper-python',
    packages=setuptools.find_packages(),
    classifiers=(
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ),
)
