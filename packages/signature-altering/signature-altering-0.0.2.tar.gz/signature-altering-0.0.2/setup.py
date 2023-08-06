from setuptools import find_packages, setup

with open('signature_altering/__init__.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.strip().split('=')[1].strip(' \'"')
            break
    else:
        version = '0.0.1'

with open('README.rst', 'rb') as f:
    readme = f.read().decode('utf-8')

REQUIRES = []

setup(
    name='signature-altering',
    version=version,
    description='Create decorators that alter the signatures of decorated functions in predictable ways',
    long_description=readme,
    author='Robin Wellner',
    author_email='rwellner0@gmail.com',
    maintainer='Robin Wellner',
    maintainer_email='rwellner0@gmail.com',
    url='https://github.com/gvx/signature-altering',
    license='MIT',

    keywords=[
        'decorators', 'generic', 'utility'
    ],

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],

    install_requires=REQUIRES,
    tests_require=['coverage', 'pytest'],

    packages=find_packages(),
)
