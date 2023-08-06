import click
import yaml
import humanize
import texttable

from datetime import datetime

def _render_table(specs, rows):
  dtypes = []
  headers = []
  align = []
  cell_fns = []
  for spec in specs:
    headers.append(spec['name'])
    align.append(spec.get('align', 'l'))
    dtypes.append(spec.get('dtype', 'a'))
    cell_fns.append(spec.get('cell'))

  table = texttable.Texttable()
  table.set_deco(texttable.Texttable.HEADER)
  table.set_cols_dtype(dtypes)
  table.set_cols_align(align)
  table.add_row(headers)
  for row in rows:
    table.add_row([cell_fn(row) for cell_fn in cell_fns])

  return table.draw()


@click.command()
@click.pass_context
def list(ctx):
  client = ctx.obj['client']
  tensorboards = client.tensorboard_list()
  if not tensorboards:
    return

  print("tensorboards", tensorboards)
  now = datetime.now()
  table = _render_table(
    [
      {'name': 'ID', 'cell': lambda o: o.id},
      {'name': 'AGE', 'cell': lambda o: humanize.naturaldelta(now - datetime.fromtimestamp(o.creationTimestamp))},
    ],
    tensorboards
  )

  print(table)

@click.command()
@click.argument("selector")
@click.option("--title", default="{id}")
@click.pass_context
def create(ctx, selector, title):
  client = ctx.obj['client']
  # TODO(adamb) Need to base this on command line options
  tensorboard_spec = {
    'sagaSelector': selector,
    'sagaTitleFormat': title,
  }
  print(client.tensorboard_create(tensorboard_spec))

@click.command()
@click.argument("tensorboard-id")
@click.pass_context
def destroy(ctx, tensorboard_id):
  client = ctx.obj['client']
  client.tensorboard_destroy(tensorboard_id)

@click.command()
@click.argument("tensorboard-id")
@click.pass_context
def show(ctx, tensorboard_id):
  client = ctx.obj['client']
  print(client.tensorboard_get(tensorboard_id))

@click.group()
def tensorboard():
  pass

tensorboard.add_command(list)
tensorboard.add_command(create)
tensorboard.add_command(destroy)
tensorboard.add_command(show)
