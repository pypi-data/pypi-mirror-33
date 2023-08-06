from setuptools import setup, find_packages

version = open('VERSION').read().strip()

setup(
    name='apodeflags',
    version=version,
    author='Felix Panozzo',
    author_email='felix@apode.se',
    url='https://github.com/apode-io/apodeflags',
    description='Simple feature flag configuration',
    long_description=open('README.md').read().strip(),
    long_description_content_type='text/markdown',
    packages=find_packages(),
    test_suite='tests',
    classifiers=(
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
    ),
)
