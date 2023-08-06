from setuptools import find_packages, setup

with open('generate_html.py', 'r') as f:
    for line in f:
        if line.startswith('__version__'):
            version = line.strip().split('=')[1].strip(' \'"')
            break
    else:
        version = '0.0.1'

with open('README.md', 'rb') as f:
    readme = f.read().decode('utf-8')

REQUIRES = ['signature-altering']

setup(
    name='generate-html',
    version=version,
    description='Generate HTML5 with Python generators',
    long_description=readme,
    long_description_content_type="text/markdown",
    author='Robin Wellner',
    author_email='rwellner0@gmail.com',
    maintainer='Robin Wellner',
    maintainer_email='rwellner0@gmail.com',
    url='https://github.com/gvx/generate-html',
    license='MIT',

    keywords=[
        'generic', 'utility', 'html'
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
    tests_require=['coverage', 'pytest', 'hypothesis'],

    packages=find_packages(),
    py_modules=['generate_html']
)
