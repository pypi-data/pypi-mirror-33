from flask import url_for
from flask.cli import FlaskGroup
import click

from pipet import create_app
from pipet.models import db, Organization, User


@click.group(cls=FlaskGroup, create_app=create_app)
def cli():
    """Management script"""


@cli.command('createuser')
@click.option('--email', prompt='Email')
@click.option('--name', prompt='Org Name')
def create_user(email, name):
    """Create an initial user"""
    org = Organization(name=name)
    user = User(email=email, organization=org)
    user.refresh_validation_hash()
    db.session.add(org)
    db.session.add(user)
    db.session.commit()

    click.echo('Login at %s' %
               url_for('pipet.login_with_validation',
                       validation_hash=user.validation_hash,
                       _external=True)
               )


@cli.command()
@click.option('--email', prompt="Email")
def login(email):
    user = User.query.filter_by(email=email).first()
    if user:
        user.refresh_validation_hash()
        db.session.add(user)
        db.session.commit()
        click.echo('Login at %s' %
                   url_for('pipet.login_with_validation',
                           validation_hash=user.validation_hash,
                           _external=True)
                   )
    else:
        click.echo('%s doesn\'t exist. Try `pipet createuser`')
