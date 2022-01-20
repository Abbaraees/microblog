import os
import click

from app import app

@app.cli.group()
def translate():
    """
    Translation and Localization commands
    """
    pass

@translate.command()
def update():
    if os.system("pybabel extract -F babel.cfg -o messages.pot ."):
        raise RuntimeError("Extract Command Failed")
    if os.system("pybabel update -i messages.pot -d app/translations"):
        raise RuntimeError("Update command failed")
    os.remove('messages.pot')

@translate.command()
def compile():
    if os.system("pybabel compile -d app/translations"):
        raise RuntimeError("Compile command failed")

@translate.command()
@click.argument('lang')
def init(lang):
    if os.system("pybabel extract -F babel.cfg -o messages.pot ."):
        raise RuntimeError("Extract Command Failed")
    if os.system(f"pybabel init -i messages.pot -d app/translations -l {lang}"):
        raise RuntimeError("Init command failed")
    os.remove('messages.pot')
