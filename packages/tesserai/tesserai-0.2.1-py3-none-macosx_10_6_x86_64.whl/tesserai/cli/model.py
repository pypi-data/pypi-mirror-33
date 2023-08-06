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

  table = texttable.Texttable(max_width=0)
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
  models = client.model_list()
  if not models:
    return

  print("models", models)
  now = datetime.now()
  table = _render_table(
    [
      {'name': 'ID', 'cell': lambda o: o.id},
      {'name': 'AGE', 'cell': lambda o: humanize.naturaldelta(now - datetime.fromtimestamp(o.creationTimestamp))},
      {'name': 'URL', 'cell': lambda o: o.url},
    ],
    models
  )

  print(table)

@click.command()
@click.pass_context
@click.argument("model-path")
def create(ctx, model_path):
  client = ctx.obj['client']
  # TODO(adamb) Need to base this on command line options
  model_spec = {
  }
  print(client.model_create(model_path))

@click.command()
@click.argument("model-id")
@click.pass_context
def destroy(ctx, model_id):
  client = ctx.obj['client']
  client.model_destroy(model_id)

@click.command()
@click.argument("model-id")
@click.pass_context
def show(ctx, model_id):
  client = ctx.obj['client']
  print(client.model_get(model_id))

@click.group()
def model():
  pass

model.add_command(list)
model.add_command(create)
model.add_command(destroy)
model.add_command(show)
