import click
import os

import tesserai.api
from tesserai.cli.auth import auth
from tesserai.cli.cluster import cluster
from tesserai.cli.tensorboard import tensorboard
from tesserai.cli.saga import saga
from tesserai.cli.model import model

from bravado.client import SwaggerClient

@click.group()
@click.pass_context
def main(ctx):
  client = tesserai.api.Client()
  ctx.ensure_object(dict)
  ctx.obj['client'] = client

main.add_command(auth)
main.add_command(cluster)
main.add_command(tensorboard)
main.add_command(saga)
main.add_command(model)
