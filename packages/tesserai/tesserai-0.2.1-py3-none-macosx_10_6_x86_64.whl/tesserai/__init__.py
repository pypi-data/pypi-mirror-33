__version__ = "0.2.1"

__title__ = "tesserai"
__description__ = "Accelerate TensorFlow with cloud GPUs in one line of code"
__uri__ = "https://github.com/tesserai/tesserai"
__doc__ = __description__ + " <" + __uri__ + ">"

__author__ = "Adam Bouhenguel"
__email__ = "adam@tesserai.com"

__license__ = ""
__copyright__ = "Copyright (c) 2018 Tesserai"

import tesserai.api as _api
import tesserai.rproxy as _rproxy

import tensorflow as tf
import time

import bravado

class RemoteCluster(object):
  def __init__(self, cluster_request, master_job=None):
    if master_job is None:
      master_job = "worker"

    if master_job not in cluster_request['jobRequests']:
      raise Exception("Master job '%s' not in given cluster_request: %r", master_job, cluster_request)

    self._cluster_request = cluster_request
    self._client = _api.Client()
    self._local_master_url = None
    self._master_job = master_job

  def _await_connected(self, master_target, retry_period):
    # Need to poll until we can run a simple session.
    config = tf.ConfigProto(gpu_options={'allow_growth': True})
    with tf.Graph().as_default() as graph:
      while True:
        # NOTE(adamb) Create a new session each time, as TF seems to leak file descriptors
        with tf.Session(master_target, config=config).as_default() as session:
          try:
            session.run(tf.constant(0))
            break
          except Exception as ex:
            ex_class_name = ex.__class__.__name__
            if ex.__class__.__module__ == "tensorflow.python.framework.errors_impl" and \
                ex_class_name == 'UnimplementedError' or ex_class_name == 'InternalError' or ex_class_name == 'UnavailableError':
              print("Remote machine(s) not ready. Sleeping before trying again...")
              print(ex, ex_class_name, ex.__class__.__module__)
              time.sleep(retry_period)
              continue
            else:
              print("Failed:", ex, ex_class_name, ex.__class__.__module__)
            raise ex

  def _ensure_connected(self):
    if self._local_master_url:
      return self._local_master_url

    try:
      self._rproxy = _rproxy.Rproxy()
      self._cluster, cluster_spec_dict = self._client.cluster_create(self._cluster_request)
      
    except bravado.exception.HTTPInternalServerError as ex:
      print("bravado.exception.HTTPInternalServerError: %s" % ex.swagger_result)
      raise ex

    default_headers = {}
    default_headers.update(self._client.auth_headers())

    proxied_ids = []
    proxied_addr_cluster_spec_dict = {name: [] for name in cluster_spec_dict.keys()}
    for name, addresses in cluster_spec_dict.items():
      for address in addresses:
        proxy_id, proxy_addr = self._rproxy.mount(address, default_headers)
        proxied_ids.append(proxy_id)
        proxied_addr_cluster_spec_dict[name].append(proxy_addr)

    self._proxied_ids = proxied_ids
    self._cluster_spec = tf.train.ClusterSpec(proxied_addr_cluster_spec_dict)
    self._local_master_url = "grpc://%s" % self._cluster_spec.task_address(self._master_job, 0)
    self._cluster_resolver = tf.contrib.cluster_resolver.SimpleClusterResolver(self._cluster_spec, self._local_master_url)
    self._cluster_id = self._cluster.id
    self._await_connected(self._local_master_url, 2)

  def get_master(self):
    self._ensure_connected()
    return self._local_master_url

  def cluster_resolver(self):
    self._ensure_connected()
    return self._cluster_resolver

  def __enter__(self):
    self._ensure_connected()
    return self

  def __exit__(self, type, value, traceback):
    self.close()

  def close(self):
    self._client.cluster_destroy(self._cluster_id)
    for proxied_id in self._proxied_ids:
      self._rproxy.unmount(proxied_id)
    self._rproxy.close()

from tensorflow.python.ops import resources as tf_py_ops_resources

class SummaryWriterSessionHook(tf.train.SessionRunHook):
  def __init__(self, summary_writer, write_graph=True):
    # HACK(adamb) This returns an op that initializes *all* summary writers, not just ours.
    #     These ops are from the *default* graph, and may not even include the given
    #     summary_writer!
    self._summary_init_op = tf.group(*tf.contrib.summary.summary_writer_initializer_op())

    self._write_graph = write_graph
    self._summary_writer = summary_writer
    self._summary_writer_resource = summary_writer._resource
    self._summary_flush_op = None
    self._began_on_graphs = set()

  def begin(self):
    # If we're called multiple times on the same graph, don't modify anything.
    # HACK(adamb) We're assuming that we won't ever be called on more than one
    # graph, since we're caching graph nodes.
    graph = tf.get_default_graph()
    if graph in self._began_on_graphs:
      return

    if self._write_graph:
      # Since there's no SessionRunHook method that can both modify the graph *and* use Session#run, we can't
      # use tf.contrib.summary.initialize(...). Instead we split its internal logic into graph modification
      # done here (in before), and Session#run (in before_run)
      with self._summary_writer.as_default():
        self._write_graph_placeholder = tf.placeholder(tf.string)
        self._write_graph_op = tf.contrib.summary.graph(self._write_graph_placeholder, 0)

    self._summary_flush_op = tf.contrib.summary.flush(writer=self._summary_writer_resource)
    self._began_on_graphs.add(graph)

  def before_run(self, run_context):
    if self._write_graph:
      session = run_context.session
      feed_dict = {
        self._write_graph_placeholder: session.graph.as_graph_def(add_shapes=True).SerializeToString()
      }
      run_context.session.run(self._write_graph_op, feed_dict)

  def after_run(self, run_context, run_values):
    run_context.session.run(self._summary_flush_op)

  def expand_scaffold(self, scaffold):
    init_op = scaffold.init_op

    # Taken from the implementation of Scaffold#finalize
    if init_op is None:
      def default_init_op():
        return tf.group(
            tf.global_variables_initializer(),
            tf_py_ops_resources.initialize_resources(tf_py_ops_resources.shared_resources()))
      init_op = tf.train.Scaffold.get_or_default(
          'init_op',
          tf.GraphKeys.INIT_OP,
          default_init_op)

    return tf.train.Scaffold(
        init_op=tf.group(
            init_op,
            self._summary_init_op),
        copy_from_scaffold=scaffold)

class MasterSessionCreator(tf.train.SessionCreator):
  """Creates a tf.Session for a dynamically generated master."""

  def __init__(self,
               master_fn,
               scaffold=None,
               config=None,
               checkpoint_dir=None,
               checkpoint_filename_with_path=None):
    """Initializes a master session creator.

    Args:
      scaffold: A `Scaffold` used for gathering or building supportive ops. If
        not specified a default one is created. It's used to finalize the graph.
      master_fn: A function that returns `String` representation of the TensorFlow master to use.
      config: `ConfigProto` proto used to configure the session.
      checkpoint_dir: A string.  Optional path to a directory where to restore
        variables.
      checkpoint_filename_with_path: Full file name path to the checkpoint file.
    """
    self._checkpoint_dir = checkpoint_dir
    self._checkpoint_filename_with_path = checkpoint_filename_with_path
    self._scaffold = scaffold or tf.train.Scaffold()
    self._session_manager = None
    self._master_fn = master_fn
    self._config = config

  def _get_session_manager(self):
    if self._session_manager:
      return self._session_manager

    self._session_manager = tf.train.SessionManager(
        local_init_op=self._scaffold.local_init_op,
        ready_op=self._scaffold.ready_op,
        ready_for_local_init_op=self._scaffold.ready_for_local_init_op,
        graph=tf.get_default_graph())
    return self._session_manager

  def create_session(self):
    self._scaffold.finalize()
    return self._get_session_manager().prepare_session(
        self._master_fn(),
        saver=self._scaffold.saver,
        checkpoint_dir=self._checkpoint_dir,
        checkpoint_filename_with_path=self._checkpoint_filename_with_path,
        config=self._config,
        init_op=self._scaffold.init_op,
        init_feed_dict=self._scaffold.init_feed_dict,
        init_fn=self._scaffold.init_fn)

class AggregatedEndSessionHook(tf.train.SessionRunHook):
  def __init__(self):
    self._fns = []

  def append(self, fn):
    self._fns.append(fn)

  def end(self, session):
    for fn in self._fns:
      fn()

def RemoteCpuSession(*, summary_writer=None, config=None, hooks=None, scaffold=None, **kwargs):
  return MonitoredRemoteClusterSession(
    cluster_fn=lambda: RemoteCpu(**kwargs),
    summary_writer=summary_writer,
    config=config,
    hooks=hooks,
    scaffold=scaffold,
  )

def RemoteV100Session(*, summary_writer=None, config=None, hooks=None, scaffold=None, **kwargs):
  return MonitoredRemoteClusterSession(
    cluster_fn=lambda: RemoteV100(**kwargs),
    summary_writer=summary_writer,
    config=config,
    hooks=hooks,
    scaffold=scaffold,
  )

def RemoteK80Session(*, summary_writer=None, config=None, hooks=None, scaffold=None, **kwargs):
  return MonitoredRemoteClusterSession(
    cluster_fn=lambda: RemoteK80(**kwargs),
    summary_writer=summary_writer,
    config=config,
    hooks=hooks,
    scaffold=scaffold,
  )

def MonitoredRemoteClusterSession(*, cluster_fn, summary_writer=None, hooks=None, config=None, scaffold=None):
  if hooks is None:
    hooks = []

  if summary_writer is not None:
    swsh = SummaryWriterSessionHook(summary_writer)
    hooks = [swsh, *hooks]
    scaffold = swsh.expand_scaffold(scaffold or tf.train.Scaffold())

  agg = AggregatedEndSessionHook()
  cluster = None
  def _create_master():
    nonlocal cluster
    if cluster is None:
      cluster = cluster_fn()
      agg.append(cluster.close)
    return cluster.get_master()

  return tf.train.MonitoredSession(
    hooks=[*hooks, agg],
    session_creator=MasterSessionCreator(
      master_fn=_create_master,
      scaffold=scaffold,
      config=config,
    ),
  )

def RemoteCpu(cpus=1, memory=1):
  return RemoteCluster({
    'jobRequests': {
      'worker': {'taskCount': 1, 'taskRequest': {'cpus': cpus, 'memory': memory}},
    },
  })

def RemoteK80(cpus=4, memory=20):
  return RemoteCluster({
    'jobRequests': {
      'worker': {'taskCount': 1, 'taskRequest': {'cpus': cpus, 'memory': memory, 'gpus': 1, 'gpuType': 'nvidia-k80'}},
    },
  })

def RemoteV100(cpus=8, memory=20):
  return RemoteCluster({
    'jobRequests': {
      'worker': {'taskCount': 1, 'taskRequest': {'cpus': cpus, 'memory': memory, 'gpus': 1, 'gpuType': 'nvidia-v100'}},
    },
  })