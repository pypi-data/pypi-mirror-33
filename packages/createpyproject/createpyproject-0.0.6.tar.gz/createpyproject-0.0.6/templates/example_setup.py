import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='{{ project_name }}',
    version='0.0.1',
    author='{{ author_name }}',
    author_email='{{ author_email }}',
    description='{{ description }}',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: {{ license }}",
        "Operating System :: OS Independent",
    ),
)
