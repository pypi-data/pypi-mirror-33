import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='createpyproject',
    version='0.0.9',
    author="Srijan Manandhar",
    author_email="srijan.manandhar@gmail.com",
    description='Test project to use python script for creating barebone python project folder structure',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/srijanss/createpy',
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    install_requires=[
        'Click',
        'jinja2',
    ],
    python_requires=">=2.7, >=3.0",
    # package_data={
    #     'createpyproject': [
    #         'example_templates/example_README.md',
    #         'example_templates/example_LICENSE.txt',
    #         'example_templates/example_setup.py',
    #         'example_templates/.gitignore',
    #         'example_templates/.travis.yml',
    #         'example_templates/Makefile',
    #         'example_templates/licenses.json'
    #     ]
    # },
    # include_package_data=True,
    entry_points='''
    [console_scripts]
    createpyproject=createpy.cli:main
    '''
)
