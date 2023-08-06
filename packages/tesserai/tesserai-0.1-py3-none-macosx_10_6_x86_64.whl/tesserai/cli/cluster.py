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
  clusters = client.cluster_list()
  if not clusters:
    return

  now = datetime.now()
  table = _render_table(
    [
      {'name': 'ID', 'cell': lambda o: o.id},
      {'name': 'STATUS', 'cell': lambda o: o.status},
      {'name': 'AGE', 'cell': lambda o: humanize.naturaldelta(now - datetime.fromtimestamp(o.creationTimestamp))},
    ],
    clusters
  )

  print(table)

@click.command()
@click.option('--tensorboard/--no-tensorboard', default=False)
@click.pass_context
def create(ctx, tensorboard):
  client = ctx.obj['client']
  # TODO(adamb) Need to base this on command line options
  cluster_spec = {
    'jobRequests': {
      'worker': {'taskCount': 1, 'taskRequest': {'cpus': 4, 'memory': 20, 'gpus': 1, 'gpuType': 'nvidia-k80'}},
    },
  }
  cluster, _ = client.cluster_create(cluster_spec)
  print(cluster)
  if tensorboard:
    tb_spec = {}
    tb = client.tensorboard_create(tb_spec)
    print(tb)

@click.command()
@click.argument("cluster-id")
@click.pass_context
def destroy(ctx, cluster_id):
  client = ctx.obj['client']
  client.cluster_destroy(cluster_id)

@click.command()
@click.argument("cluster-id")
@click.pass_context
def show(ctx, cluster_id):
  client = ctx.obj['client']
  print(client.cluster_get(cluster_id))

@click.group()
def cluster():
  pass

cluster.add_command(list)
cluster.add_command(create)
cluster.add_command(destroy)
cluster.add_command(show)
