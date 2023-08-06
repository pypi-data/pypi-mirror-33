import click
import os.path

@click.command()
@click.pass_context
def status(ctx):
  client = ctx.obj['client']
  

@click.command()
@click.pass_context
@click.option('--overwrite/--no-overwrite', default=False)
@click.option('--subscription-id', default=None)
def init(ctx, overwrite, subscription_id):
  client = ctx.obj['client']
  print(client.auth_init(overwrite=overwrite, subscription_id=subscription_id))

@click.group()
def auth():
  pass

auth.add_command(status)
auth.add_command(init)
