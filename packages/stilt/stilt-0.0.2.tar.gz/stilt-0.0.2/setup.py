import setuptools


with open('README.md', 'r') as readme:
    long_description = readme.read()

setuptools.setup(
    name='stilt',
    version='0.0.2',
    author='Stilt Contributors',
    author_email='python.stilt@bdubeit.com',
    description='Python project configreator',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/bdube/stilt',
    packages=setuptools.find_packages(),
    classifiers=(
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: Apache Software License',
        'Development Status :: 1 - Planning'
    )
)
