import os
import sys
import json
import subprocess
from datetime import datetime
import click

from jinja2 import Environment, FileSystemLoader, select_autoescape

# ENVIRONMENT VARIABLES
os.environ['README_MD'] = 'example_README.md.txt'
os.environ['SETUP_PY'] = 'example_setup.py'
os.environ['LICENSE_TXT'] = 'example_LICENSE.txt'
os.environ['GITIGNORE'] = '.gitignore.txt'
os.environ['TRAVIS_YML'] = '.travis.yml.txt'
os.environ['MAKEFILE'] = 'Makefile.txt'

default_dir = os.path.abspath(os.getcwd())
project_base_dir = os.sep.join(os.path.abspath(os.path.dirname(__file__)).split(os.sep)[:-1])

def create_initpy(folder_name):
    cmd = ['touch', folder_name + os.sep + '__init__.py']
    subprocess.Popen(cmd).wait()

def create_project_folder(project):
    try:
        os.mkdir(project)
        try:
            os.mkdir(project + os.sep + project)
            create_initpy(project + os.sep + project)
        except FileExistsError:
            create_initpy(project + os.sep + project)
    except FileExistsError as error:
        override = click.prompt(
            f'Project name {project} already exists.\n' + 'Override old project? { 0: No, 1: Yes }',
            default='1'
        )
        if not int(override):
            sys.exit(0)

def create_test_folder(project):
    os.chdir(project)
    try:
        os.mkdir('tests')
        create_initpy('tests')
    except FileExistsError:
        create_initpy('tests')
    finally:
        os.chdir(default_dir)

def get_license(index):
    with open(project_base_dir + os.sep + 'example_templates/licenses.txt', 'r') as f:
        licenselist = f.read()
    if licenselist:
        licenselist = json.loads(licenselist)[index]
    return { 'key': licenselist['key'], 'body': licenselist['body'] }

def render_file(template_file, **kwargs):
    """
    render template files with given context arguments
    """ 
    env = Environment(
        loader=FileSystemLoader(project_base_dir + os.sep + 'example_templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template(template_file)
    current_year = datetime.strftime(datetime.now(), '%Y')
    rendered_template = template.render(
        year=current_year,
        project_name=kwargs['project_name'],
        description=kwargs['description'],
        long_description=kwargs['long_description'],
        author_name=kwargs['author_name'],
        author_email=kwargs['author_email'],
        license=get_license(kwargs['license'])['key'].upper()
    )
    return rendered_template

def add_template_to_project(filename, template, project):
    if os.path.abspath(project) != os.path.abspath(os.getcwd()):
        os.chdir(os.path.abspath(project))
        if filename == '__init__.py':
            os.chdir(os.path.abspath(project))
    if 'example' in filename:
        template_filename = filename.split('_')[1] 
    else:
        template_filename = filename
    # extract txt extension from all files
    if template_filename.split('.')[-1] != 'py':
        template_filename = '.'.join(template_filename.split('.')[:-1])
    with open(template_filename, 'w') as f:
        f.write(template)
    os.chdir(default_dir)

@click.group()
@click.pass_context
def main(ctx):
    ctx.obj = {
        'project': 'test_project',
        'description': 'Test Project',
        'long_description': 'Test python project.',
        'author': 'testUser',
        'email': 'test@example.com',
        'license': 0 # 0: MIT, 1: Apache 2.0
    }

@main.command()
@click.pass_context
def create(ctx):
    # with open('licenses.json' , 'r') as fb:
    #     licenselist = fb.read()
    kwargs = {}
    kwargs['project_name'] = click.prompt(
        'Please enter your project name',
        default=ctx.obj['project']
    )
    click.echo(kwargs['project_name'])
    kwargs['description'] = click.prompt(
        'Project Description',
        default=ctx.obj['description']      
    ) 
    click.echo(kwargs['description'])
    kwargs['long_description'] = click.prompt(
        'Project Detail Description',
        default=ctx.obj['long_description']      
    )
    click.echo(kwargs['long_description'])
    kwargs['author_name'] = click.prompt(
        'Author Name',
        default=ctx.obj['author']      
    )
    click.echo(kwargs['author_name'])
    kwargs['author_email'] = click.prompt(
        'Author Email',
        default=ctx.obj['email']      
    )
    click.echo(kwargs['author_email'])
    kwargs['license'] = click.prompt(
        'License { 0: MIT, 1: Apache 2.0 }',
        default=ctx.obj['license']      
    )

    # Create Project Folder
    create_project_folder(kwargs['project_name'])
    # Create example license file with choosen license
    with open(project_base_dir + os.sep + 'example_templates' + os.sep + os.getenv('LICENSE_TXT'), 'w') as f:
        f.write(get_license(kwargs['license'])['body'])
    # Copy project files
    project_files = (
        os.getenv('README_MD'),
        os.getenv('SETUP_PY'),
        os.getenv('LICENSE_TXT'),
        os.getenv('GITIGNORE'),
        os.getenv('TRAVIS_YML'),
        os.getenv('MAKEFILE'),
    )
    for project_file in project_files:
        template = render_file(project_file, **kwargs)
        add_template_to_project(project_file, template, kwargs['project_name'])

    # Create test folder
    create_test_folder(kwargs['project_name'])

if __name__ == '__main__':
    main()