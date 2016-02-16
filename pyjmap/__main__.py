import sys
import os.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import click
from pyjmap import app, database
from functools import update_wrapper


def with_db(f):
    @click.pass_context
    def result(ctx, *args, **kwargs):
        with app.app_context():
            result = ctx.invoke(f, *args, **kwargs)
            database.commit()
            return result
    return update_wrapper(result, f)


@click.group()
def cli():
    pass


@cli.command()
def run():
    app.run(debug=True)


@cli.group("user")
def cli_user():
    pass

@cli_user.command("add")
@click.argument("name")
@click.option("--password",
              prompt=True,
              hide_input=True,
              confirmation_prompt=True)
@with_db
def user_add(name, password):
    user = database.User()
    user.username = name
    user.setPassword(password)
    user.save()


@cli.group("db")
def cli_db():
    pass

@cli_db.command("create")
@with_db
def db_create():
    database.db.create_all()
