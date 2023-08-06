import click
import os
from os import environ
import subprocess
import urllib2
import re
import git

@click.group()
def cli():
    pass

@cli.command()
@click.pass_context
def init(ctx):
    """ Initalise a new subscribie project """
    click.echo("Initalising a new subscribie project")
    # Get example .env file, rename & place it in current working directory
    click.echo("... getting example .env file")
    response = urllib2.urlopen('https://raw.githubusercontent.com/KarmaComputing/subscribie/master/subscribie/.env.example')
    envfile = response.read()
    with open('.env', 'wb') as fh:
        fh.write(envfile)

    # Get example jamla.yaml file, rename & place it in current working directory
    click.echo("... getting example jamla.yaml file")
    response = urllib2.urlopen('https://raw.githubusercontent.com/KarmaComputing/subscribie/master/subscribie/jamla.yaml.example')
    jamlafile = response.read()
    with open('jamla.yaml', 'wb') as fh:
        fh.write(jamlafile)
    # Replace static assets path
    with open('jamla.yaml', 'r+') as fh:
        jamla = fh.read()
        static_folder = ''.join([os.getcwd(), '/themes/theme-jesmond/static/'])
        jamla = re.sub(r'static_folder:.*', 'static_folder: ' + static_folder, jamla)
    os.unlink('jamla.yaml')
    # Write jamla file
    with open('jamla.yaml', 'w') as fh:
        fh.write(jamla)
    try:
        os.mkdir('themes')
    except OSError:
        click.echo("Warning: Failed to create themes directory", err=True)
    # Git clone default template
    try:
        click.echo("... cloning default template")
        git.Git('themes/').clone('git@github.com:Subscribie/theme-jesmond.git')
    except Exception as inst:
        click.echo("Warning: Failed to clone default theme. Perhaps it's already cloned?", err=True)

    # Edit .env file with correct paths
    fp = open('.env', 'a+')
    fp.write(''.join(['JAMLA_PATH="', os.getcwd(), '/', 'jamla.yaml"', "\n"]))
    fp.write(''.join(['TEMPLATE_FOLDER="', os.getcwd(), '/themes/"', "\n"]))
    fp.close()
    ctx.invoke(initdb)
    click.echo("Done")

@cli.command()
def initdb():
    """ Initalise the database """
    if os.path.isfile('data.db'):
        click.echo('Error: data.db already exists.', err=True)
        return -1

    with open('data.db', 'w'):
        click.echo('... creating data.db')
        pass
    click.echo('... running initial database creation script')
    response = urllib2.urlopen('https://raw.githubusercontent.com/KarmaComputing/subscribie/master/subscribie/createdb.py')
    createdb = response.read()
    exec(createdb) #TODO change all these to migrations
    click.echo("... fetching migrations, this might take a while")
    try:
        git.Git().clone('git@github.com:KarmaComputing/subscribie.git')
    except Exception as inst:
        click.echo("Warning: Failed to clone subscribie migrations")
    click.echo("... running migrations")
    migrationsDir = 'subscribie/subscribie/migrations'
    for root, dirs, files in os.walk(migrationsDir):
        files.sort()
        for name in files:
            migration = os.path.join(root, name)
            click.echo("... running migration: " + name)
            subprocess.call("python " + migration + ' -up -db ./data.db', shell=True)
    
@cli.command()
def migrate():
    """ Run latest migrations """

@cli.command()
def run():
    """Run subscribie"""
    environ['FLASK_APP'] = 'subscribie'
    click.echo('Running subscribie...')
    subprocess.call("flask run", shell=True)

if __name__ == '__main__':
    cli()
