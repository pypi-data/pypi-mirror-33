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
  sagas = client.saga_list()
  if not sagas:
    return

  print("sagas", sagas)
  now = datetime.now()
  table = _render_table(
    [
      {'name': 'ID', 'cell': lambda o: o.id},
      {'name': 'AGE', 'cell': lambda o: humanize.naturaldelta(now - datetime.fromtimestamp(o.creationTimestamp))},
    ],
    sagas
  )

  print(table)

@click.command()
@click.pass_context
def create(ctx):
  client = ctx.obj['client']
  # TODO(adamb) Need to base this on command line options
  saga_spec = {
  }
  print(client.saga_create(saga_spec))

@click.command()
@click.argument("saga-id")
@click.pass_context
def destroy(ctx, saga_id):
  client = ctx.obj['client']
  client.saga_destroy(saga_id)

@click.command()
@click.argument("saga-id")
@click.pass_context
def show(ctx, saga_id):
  client = ctx.obj['client']
  print(client.saga_get(saga_id))

@click.group()
def saga():
  pass

saga.add_command(list)
saga.add_command(create)
saga.add_command(destroy)
saga.add_command(show)
